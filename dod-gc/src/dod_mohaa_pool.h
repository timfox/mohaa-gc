/* A fixed region the script VM allocates from, instead of the engine heap.
 *
 * On GameCube the engine heap is fragmented by the time a big level has loaded (m1l1 leaves 35 KB free in
 * 11 pieces), so the compiler's blocks and the VM's tables fail there even though the VM is far under its
 * budget. The backend can instead hand the VM one region (the engine's map-load arena tail, which lives as
 * long as the level and so as long as the VM).
 *
 * Boundary tags: every block has a header and footer holding its size with bit 0 set while in use, so free
 * merges a block with free neighbours. The pool can span several regions (a short arena gives pieces). Free blocks sit on a list kept in address order. Normally a request
 * takes the lowest free block that fits, from its front, so long-lived data packs at the bottom. While the
 * VM compiles (MohaaPool_Top on) requests take the highest block that fits, from its end: the compiler's
 * scratch then lives at the top and leaves one hole when it is freed, instead of holes between the
 * bytecode of every script (m1l1 ran out with 188 KB free, largest piece 7 KB, before this).
 * All static: included by dod_mohaa.c only.
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

#define MOHAA_POOL_REGIONS 8

typedef struct MohaaPool {
	unsigned char *base;         /* first region's blocks (rbase[0]) */
	size_t size;                 /* bytes of blocks in all regions */
	unsigned char *rbase[MOHAA_POOL_REGIONS];   /* each region's first block, and its span */
	size_t rsize[MOHAA_POOL_REGIONS];
	int nregions;
	MohaaPoolFree *free, *tail;  /* free blocks, lowest address first */
	size_t used;                 /* bytes in use, headers included */
	int top;                     /* take new blocks from the top of the region */
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
	else
		p->tail = f->prev;
}

/* Put a free block of size bytes at blk on the list, after prev (NULL: first). */
static void mp_insert(MohaaPool *p, unsigned char *blk, size_t size, MohaaPoolFree *prev)
{
	MohaaPoolFree *f = (MohaaPoolFree *)(void *)blk;
	mp_tag(blk, size, 0);
	f->prev = prev;
	f->next = prev ? prev->next : p->free;
	if (f->next)
		f->next->prev = f;
	else
		p->tail = f;
	if (prev)
		prev->next = f;
	else
		p->free = f;
}

/* The free block just below blk in address order, or NULL. */
static MohaaPoolFree *mp_below(const MohaaPool *p, const unsigned char *blk)
{
	MohaaPoolFree *f = p->tail;
	while (f && (const unsigned char *)f > blk)
		f = f->prev;
	return f;
}

static void mp_release(MohaaPool *p, unsigned char *blk, size_t size);

/* Add a region: its start and size are trimmed to the alignment, and a busy tag at each end keeps free from
 * merging a block across the region's edge, so regions need not touch. Returns 0 when it is too small to use. */
static int MohaaPool_AddRegion(MohaaPool *p, void *region, size_t size)
{
	const size_t one = 1;   /* a size-0 block in use */
	uintptr_t a = ((uintptr_t)region + MP_ALIGN - 1) & ~(uintptr_t)(MP_ALIGN - 1);
	size_t span;
	if (!region || p->nregions >= MOHAA_POOL_REGIONS || size < (size_t)(a - (uintptr_t)region) + 2 * MP_TAG + MP_MIN)
		return 0;
	size -= (size_t)(a - (uintptr_t)region);
	span = (size - 2 * MP_TAG) & ~(size_t)(MP_ALIGN - 1);
	if (span < MP_MIN)
		return 0;
	memcpy((unsigned char *)a, &one, MP_TAG);
	memcpy((unsigned char *)a + MP_TAG + span, &one, MP_TAG);
	p->rbase[p->nregions] = (unsigned char *)a + MP_TAG;
	p->rsize[p->nregions] = span;
	if (!p->nregions)
		p->base = p->rbase[0];
	p->nregions++;
	p->size += span;
	mp_release(p, (unsigned char *)a + MP_TAG, span);
	return 1;
}

static int MohaaPool_Init(MohaaPool *p, void *region, size_t size)
{
	memset(p, 0, sizeof(*p));
	return MohaaPool_AddRegion(p, region, size);
}

static void MohaaPool_Top(MohaaPool *p, int on) { p->top = on; }

static size_t mp_need(size_t n)
{
	size_t need = (n + 2 * MP_TAG + MP_ALIGN - 1) & ~(size_t)(MP_ALIGN - 1);
	return need < MP_MIN ? MP_MIN : need;
}

/* Take need bytes from the free block f: from its front, or its end when top. A remainder big enough to
   be a block stays free, in f's place on the list. */
static unsigned char *mp_take(MohaaPool *p, MohaaPoolFree *f, size_t need, int top)
{
	unsigned char *blk = (unsigned char *)f;
	const size_t have = mp_size(blk);
	MohaaPoolFree *prev = f->prev;
	if (have - need < MP_MIN) {
		mp_unlink(p, f);
		mp_tag(blk, have, 1);
		p->used += have;
		return blk;
	}
	if (top) {
		mp_tag(blk, have - need, 0);   /* f keeps its links */
		blk += have - need;
	} else {
		mp_unlink(p, f);
		mp_insert(p, blk + need, have - need, prev);
	}
	mp_tag(blk, need, 1);
	p->used += need;
	return blk;
}

static void *MohaaPool_Alloc(MohaaPool *p, size_t n)
{
	const size_t need = mp_need(n);
	MohaaPoolFree *f;
	if (!n || need < n)
		return NULL;
	if (p->top) {
		for (f = p->tail; f; f = f->prev)
			if (mp_size(f) >= need)
				return mp_take(p, f, need, 1) + MP_TAG;
	} else {
		for (f = p->free; f; f = f->next)
			if (mp_size(f) >= need)
				return mp_take(p, f, need, 0) + MP_TAG;
	}
	return NULL;
}

/* Free the block at blk of size bytes, merging with free neighbours. */
static void mp_release(MohaaPool *p, unsigned char *blk, size_t size)
{
	unsigned char *end = blk + size;
	MohaaPoolFree *next = NULL, *prev;
	size_t below;
	if (!mp_busy(end)) {   /* a region's last block meets its end tag, which is busy */
		next = (MohaaPoolFree *)(void *)end;
		size += mp_size(end);
	}
	memcpy(&below, blk - MP_TAG, MP_TAG);
	if (!(below & 1u)) {   /* the block below is free: it grows over this one, keeping its place */
		if (next)
			mp_unlink(p, next);
		mp_tag(blk - below, below + size, 0);
		return;
	}
	if (next) {
		prev = next->prev;
		mp_unlink(p, next);
	} else {
		prev = mp_below(p, blk);
	}
	mp_insert(p, blk, size, prev);
}

static void MohaaPool_Free(MohaaPool *p, void *ptr)
{
	unsigned char *blk;
	size_t size;
	if (!ptr)
		return;
	blk = (unsigned char *)ptr - MP_TAG;
	size = mp_size(blk);
	p->used -= size;
	mp_release(p, blk, size);
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
	/* grow in place into a free neighbour above */
	if (need > have && !mp_busy(end) && have + mp_size(end) >= need) {
		MohaaPoolFree *f = (MohaaPoolFree *)(void *)end;
		const size_t fsize = mp_size(end);
		MohaaPoolFree *prev = f->prev;
		size_t grown = have + fsize;
		mp_unlink(p, f);
		if (grown - need >= MP_MIN) {
			mp_insert(p, blk + need, grown - need, prev);
			grown = need;
		}
		mp_tag(blk, grown, 1);
		p->used += grown - have;
		return ptr;
	}
	if (need <= have) {
		if (have - need >= MP_MIN) {   /* give the tail back */
			mp_tag(blk, need, 1);
			p->used -= have - need;
			mp_release(p, blk + need, have - need);
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
