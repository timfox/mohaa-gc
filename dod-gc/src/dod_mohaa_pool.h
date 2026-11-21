/* A fixed region the script VM allocates from, instead of the engine heap.
 *
 * On GameCube the engine heap is fragmented by the time a big level has loaded (m1l1 leaves 35 KB free in
 * 11 pieces), so the compiler's blocks and the VM's tables fail there even though the VM is far under its
 * budget. The backend can instead hand the VM one region (the engine's map-load arena tail, which lives as
 * long as the level and so as long as the VM). This is a boundary-tag first-fit allocator over that region:
 * every block has a header and footer holding its size with bit 0 set while in use; free blocks are also on
 * a doubly linked list, and free merges a block with free neighbours so the region does not fragment the way
 * the heap did. All static: included by dod_mohaa.c only.
 */
#ifndef DOD_MOHAA_POOL_H
#define DOD_MOHAA_POOL_H

#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef struct MohaaPoolFree {
	size_t head;
	struct MohaaPoolFree *prev, *next;
} MohaaPoolFree;

typedef struct MohaaPool {
	unsigned char *base;
	size_t size;
	MohaaPoolFree *free;
	size_t used;  /* bytes in use, headers included */
} MohaaPool;

#define MP_ALIGN 8u
#define MP_TAG sizeof(size_t)
/* smallest block: header, the free-list links and a footer */
#define MP_MIN (((sizeof(MohaaPoolFree) + MP_TAG) + MP_ALIGN - 1) & ~(size_t)(MP_ALIGN - 1))

static size_t mp_size(const void *blk) { return *(const size_t *)blk & ~(size_t)1; }
static int mp_busy(const void *blk) { return (int)(*(const size_t *)blk & 1u); }

static void mp_tag(unsigned char *blk, size_t size, int busy)
{
	const size_t t = size | (busy ? 1u : 0u);
	memcpy(blk, &t, MP_TAG);
	memcpy(blk + size - MP_TAG, &t, MP_TAG);
}

static void mp_unlink(MohaaPool *p, MohaaPoolFree *f)
{
	if (f->prev)
		f->prev->next = f->next;
	else
		p->free = f->next;
	if (f->next)
		f->next->prev = f->prev;
}

static void mp_push(MohaaPool *p, unsigned char *blk, size_t size)
{
	MohaaPoolFree *f = (MohaaPoolFree *)(void *)blk;
	mp_tag(blk, size, 0);
	f->prev = NULL;
	f->next = p->free;
	if (p->free)
		p->free->prev = f;
	p->free = f;
}

/* Region start and size are trimmed to the alignment. Returns 0 when the region is too small to use. */
static int MohaaPool_Init(MohaaPool *p, void *region, size_t size)
{
	uintptr_t a = ((uintptr_t)region + MP_ALIGN - 1) & ~(uintptr_t)(MP_ALIGN - 1);
	memset(p, 0, sizeof(*p));
	if (!region || size < (size_t)(a - (uintptr_t)region) + MP_MIN)
		return 0;
	size -= (size_t)(a - (uintptr_t)region);
	size &= ~(size_t)(MP_ALIGN - 1);
	p->base = (unsigned char *)a;
	p->size = size;
	mp_push(p, p->base, size);
	return 1;
}

static size_t mp_need(size_t n)
{
	size_t need = (n + 2 * MP_TAG + MP_ALIGN - 1) & ~(size_t)(MP_ALIGN - 1);
	return need < MP_MIN ? MP_MIN : need;
}

/* Take need bytes from the front of the free block f; a remainder big enough to be a block stays free. */
static unsigned char *mp_take(MohaaPool *p, MohaaPoolFree *f, size_t need)
{
	unsigned char *blk = (unsigned char *)f;
	const size_t have = mp_size(blk);
	mp_unlink(p, f);
	if (have - need >= MP_MIN) {
		mp_tag(blk, need, 1);
		mp_push(p, blk + need, have - need);
	} else {
		need = have;
		mp_tag(blk, need, 1);
	}
	p->used += need;
	return blk;
}

static void *MohaaPool_Alloc(MohaaPool *p, size_t n)
{
	const size_t need = mp_need(n);
	MohaaPoolFree *f;
	if (!n || need < n)
		return NULL;
	for (f = p->free; f; f = f->next)
		if (mp_size(f) >= need)
			return mp_take(p, f, need) + MP_TAG;
	return NULL;
}

static void MohaaPool_Free(MohaaPool *p, void *ptr)
{
	unsigned char *blk, *end;
	size_t size;
	if (!ptr)
		return;
	blk = (unsigned char *)ptr - MP_TAG;
	size = mp_size(blk);
	p->used -= size;
	end = blk + size;
	if (end < p->base + p->size && !mp_busy(end)) {
		mp_unlink(p, (MohaaPoolFree *)(void *)end);
		size += mp_size(end);
	}
	if (blk > p->base) {
		size_t prev;
		memcpy(&prev, blk - MP_TAG, MP_TAG);
		if (!(prev & 1u)) {
			blk -= prev;
			mp_unlink(p, (MohaaPoolFree *)(void *)blk);
			size += prev;
		}
	}
	mp_push(p, blk, size);
}

static void *MohaaPool_Realloc(MohaaPool *p, void *ptr, size_t n)
{
	unsigned char *blk, *end;
	size_t have, need;
	void *q;
	if (!ptr)
		return MohaaPool_Alloc(p, n);
	if (!n) {
		MohaaPool_Free(p, ptr);
		return NULL;
	}
	blk = (unsigned char *)ptr - MP_TAG;
	have = mp_size(blk);
	need = mp_need(n);
	if (need < n)
		return NULL;
	end = blk + have;
	/* grow in place into a free neighbour */
	if (need > have && end < p->base + p->size && !mp_busy(end) && have + mp_size(end) >= need) {
		const size_t merged = have + mp_size(end);
		mp_unlink(p, (MohaaPoolFree *)(void *)end);
		mp_tag(blk, merged, 1);
		p->used += merged - have;
		have = merged;
	}
	if (need <= have) {
		if (have - need >= MP_MIN) {  /* give the tail back */
			mp_tag(blk, need, 1);
			p->used -= have - need;
			mp_push(p, blk + need, have - need);
			/* merge the returned tail with what follows it */
			{
				unsigned char *tail = blk + need, *after = tail + mp_size(tail);
				if (after < p->base + p->size && !mp_busy(after)) {
					const size_t t = mp_size(tail) + mp_size(after);
					mp_unlink(p, (MohaaPoolFree *)(void *)after);
					mp_unlink(p, (MohaaPoolFree *)(void *)tail);
					mp_push(p, tail, t);
				}
			}
		}
		return ptr;
	}
	q = MohaaPool_Alloc(p, n);
	if (!q)
		return NULL;
	memcpy(q, ptr, have - 2 * MP_TAG);
	MohaaPool_Free(p, ptr);
	return q;
}

/* Largest single allocation that would succeed now. */
static size_t MohaaPool_Largest(const MohaaPool *p)
{
	size_t best = 0;
	const MohaaPoolFree *f;
	for (f = p->free; f; f = f->next)
		if (mp_size(f) > best)
			best = mp_size(f);
	return best > 2 * MP_TAG ? best - 2 * MP_TAG : 0;
}

#endif
