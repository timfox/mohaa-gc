/* dod_mohaa_paths.h - MOHAA path nodes for DoD-GC, included once by dod_mohaa.c (all static).
 *
 * MOHAA info_pathnodes come from maps/<map>.nodes, written by mohaa-gc tools/bsp19_to_map.py. They are
 * not entities: a node costs no edict, 32 bytes here plus 10 bytes of search scratch. Links are made once
 * at level load with one walkable() test per pair tried; a soldier's move order then walks node to node,
 * one A* per node reached (see route_* in dod_mohaa.c). */
#ifndef MOHAA_PATHS_H
#define MOHAA_PATHS_H

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MOHAA_PATH_MAX 2048		/* nodes kept per map; the rest of a bigger map's nodes are dropped */
#define MOHAA_PATH_LINKS 8		/* neighbours per node */
#define MOHAA_PATH_TRIES 16		/* nearest candidates traced per node at link time */
#define MOHAA_PATH_REACH 400.0f		/* farthest link (MOHAA links nodes up to 512 units; x72/94 is 392) */
#define MOHAA_PATH_NONE 0xFFFF

typedef void *(*MohaaPathsAlloc)(void *ptr, size_t old_size, size_t new_size);

typedef struct MohaaPaths {
	int count;
	float (*pos)[3];			/* feet, GoldSrc units */
	uint32_t *name;				/* MohaaPaths_Hash of the targetname, 0 none */
	unsigned short (*link)[MOHAA_PATH_LINKS];	/* MOHAA_PATH_NONE past the last */
	float *cost;				/* search scratch */
	unsigned short *from, *heap, *slot;
	void *block;				/* one allocation holds all of it */
	size_t block_size;
	MohaaPathsAlloc alloc;
} MohaaPaths;

typedef int (*MohaaPathWalkable)(void *ctx, const float a[3], const float b[3]);
typedef int (*MohaaPathEdgeBlocked)(void *ctx, const float a[3], const float b[3]);

/* ---- path nodes ---- */

static uint32_t MohaaPaths_Hash(const char *name)
{
	uint32_t h = 2166136261u;
	for (; *name; name++) {
		unsigned char c = (unsigned char)*name;
		if (c >= 'A' && c <= 'Z')
			c = (unsigned char)(c - 'A' + 'a');
		h = (h ^ c) * 16777619u;
	}
	return h ? h : 1;
}

static void MohaaPaths_Free(MohaaPaths *g)
{
	if (g->block) {
		if (g->alloc)
			g->alloc(g->block, g->block_size, 0);
		else
			free(g->block);
	}
	memset(g, 0, sizeof(*g));
}

/* the next line of text into buf (cut to fit), the cursor moved past it; 0 at the end */
static int path_next_line(const char **at, const char *end, char *buf, size_t size)
{
	const char *s = *at;
	size_t n = 0;
	if (s >= end)
		return 0;
	while (s < end && *s != '\n' && *s != '\0') {
		if (n + 1 < size)
			buf[n++] = *s;
		s++;
	}
	buf[n] = '\0';
	*at = s < end ? s + 1 : end;
	if (s < end && *s == '\0')
		*at = end;
	return 1;
}

static int MohaaPaths_Load(MohaaPaths *g, const char *text, size_t len, MohaaPathsAlloc alloc)
{
	const char *end = text + len, *at = text;
	char line[512], name[96];
	float v[3];
	size_t bytes;
	int n = 0, k = 0;
	memset(g, 0, sizeof(*g));
	g->alloc = alloc;
	while (path_next_line(&at, end, line, sizeof(line)))
		if (line[0] != '#' && sscanf(line, "%f %f %f", &v[0], &v[1], &v[2]) == 3)
			n++;
	if (n > MOHAA_PATH_MAX)
		n = MOHAA_PATH_MAX;
	if (n <= 0)
		return 0;
	{
		const size_t pos = sizeof(float) * 3 * (size_t)n, nm = sizeof(uint32_t) * (size_t)n;
		const size_t lk = sizeof(unsigned short) * MOHAA_PATH_LINKS * (size_t)n, cost = sizeof(float) * (size_t)n;
		char *b;
		bytes = pos + nm + cost + lk + sizeof(unsigned short) * 3 * (size_t)n;
		g->block_size = bytes;
		b = (char *)(alloc ? alloc(NULL, 0, bytes) : malloc(bytes));
		if (!b) {
			g->block_size = 0;
			g->alloc = NULL;
			return -n;
		}
		g->block = b;
		g->pos = (float (*)[3])b;
		g->name = (uint32_t *)(b + pos);
		g->cost = (float *)(b + pos + nm);
		g->link = (unsigned short (*)[MOHAA_PATH_LINKS])(b + pos + nm + cost);
		g->from = (unsigned short *)(b + pos + nm + cost + lk);
		g->heap = g->from + n;
		g->slot = g->heap + n;
		memset(g->link, 0xFF, lk);
	}
	at = text;
	while (k < n && path_next_line(&at, end, line, sizeof(line))) {
		int grav, flags;
		if (line[0] == '#' || sscanf(line, "%f %f %f", &v[0], &v[1], &v[2]) != 3)
			continue;
		memcpy(g->pos[k], v, sizeof(v));
		g->name[k] = 0;
		if (sscanf(line, "%*f %*f %*f %d %d %95s", &grav, &flags, name) == 3 && strcmp(name, "-"))
			g->name[k] = MohaaPaths_Hash(name[0] == '$' ? name + 1 : name);
		k++;
	}
	g->count = k;
	return k;
}

/* "%20" -> ' ', "%25" -> '%' (any %XX), in place */
static void path_unescape(char *s)
{
	char *o = s;
	for (; *s; s++) {
		int hi, lo;
		if (s[0] == '%' && s[1] && s[2] &&
		    (hi = s[1] <= '9' ? s[1] - '0' : (s[1] | 32) - 'a' + 10) >= 0 && hi < 16 &&
		    (lo = s[2] <= '9' ? s[2] - '0' : (s[2] | 32) - 'a' + 10) >= 0 && lo < 16) {
			*o++ = (char)(hi * 16 + lo);
			s += 2;
		} else
			*o++ = *s;
	}
	*o = 0;
}

/* The script-only keys of each node, "#key=value" tokens after the name (the converter writes MOHAA's #set,
 * #group ... there, with space and % escaped). key(ctx, node index, "#set", "3") for each, in Load's node order. */
static void MohaaPaths_Keys(const char *text, size_t len, int count,
	void (*key)(void *ctx, int node, const char *k, const char *v), void *ctx)
{
	const char *end = text + len, *at = text;
	char line[512];
	float v[3];
	int k = 0;
	while (k < count && path_next_line(&at, end, line, sizeof(line))) {
		char *p = line;
		int field = 0;
		if (line[0] == '#' || sscanf(line, "%f %f %f", &v[0], &v[1], &v[2]) != 3)
			continue;
		for (;;) {
			char *tok, *eq;
			while (*p == ' ' || *p == '\t' || *p == '\r')
				p++;
			if (!*p)
				break;
			tok = p;
			while (*p && *p != ' ' && *p != '\t' && *p != '\r')
				p++;
			if (*p)
				*p++ = 0;
			if (field++ < 6 || tok[0] != '#' || !(eq = strchr(tok, '=')))
				continue;
			*eq = 0;
			path_unescape(tok);
			path_unescape(eq + 1);
			key(ctx, k, tok, eq + 1);
		}
		k++;
	}
}

static float path_dist2(const float a[3], const float b[3])
{
	const float dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
	return dx * dx + dy * dy + dz * dz;
}

static int path_links(const MohaaPaths *g, int i)
{
	int n = 0;
	while (n < MOHAA_PATH_LINKS && g->link[i][n] != MOHAA_PATH_NONE)
		n++;
	return n;
}

static int path_linked(const MohaaPaths *g, int i, int j)
{
	int k;
	for (k = 0; k < MOHAA_PATH_LINKS && g->link[i][k] != MOHAA_PATH_NONE; k++)
		if (g->link[i][k] == j)
			return 1;
	return 0;
}

static int MohaaPaths_Link(MohaaPaths *g, MohaaPathWalkable walkable, void *ctx, float reach)
{
	int traces = 0, i, j, k;
	for (i = 0; i < g->count; i++) {
		int cand[MOHAA_PATH_TRIES], nc = 0;
		float cd[MOHAA_PATH_TRIES];
		/* the nearest few inside reach, nearest first */
		for (j = 0; j < g->count; j++) {
			const float d = path_dist2(g->pos[i], g->pos[j]);
			if (j == i || d > reach * reach)
				continue;
			if (nc == MOHAA_PATH_TRIES && d >= cd[nc - 1])
				continue;
			k = nc < MOHAA_PATH_TRIES ? nc++ : nc - 1;
			while (k > 0 && cd[k - 1] > d) {
				cd[k] = cd[k - 1];
				cand[k] = cand[k - 1];
				k--;
			}
			cd[k] = d;
			cand[k] = j;
		}
		for (k = 0; k < nc && path_links(g, i) < MOHAA_PATH_LINKS; k++) {
			j = cand[k];
			if (path_linked(g, i, j) || path_links(g, j) >= MOHAA_PATH_LINKS)
				continue;
			traces++;
			if (!walkable(ctx, g->pos[i], g->pos[j]))
				continue;
			g->link[i][path_links(g, i)] = (unsigned short)j;
			g->link[j][path_links(g, j)] = (unsigned short)i;
		}
	}
	return traces;
}

static int MohaaPaths_Find(const MohaaPaths *g, const char *name)
{
	const uint32_t h = MohaaPaths_Hash(name[0] == '$' ? name + 1 : name);
	int i;
	for (i = 0; i < g->count; i++)
		if (g->name[i] == h)
			return i;
	return -1;
}

static int MohaaPaths_Nearest(const MohaaPaths *g, const float p[3])
{
	int best = -1, i;
	float bd = 0.0f;
	for (i = 0; i < g->count; i++) {
		const float dx = g->pos[i][0] - p[0], dy = g->pos[i][1] - p[1], dz = (g->pos[i][2] - p[2]) * 2.0f;
		const float d = dx * dx + dy * dy + dz * dz;
		if (best < 0 || d < bd) {
			best = i;
			bd = d;
		}
	}
	return best;
}

/* the search's open list: a binary heap on cost + straight-line distance to the target, with each node's heap slot */
static float path_heap_key(const MohaaPaths *g, int n, int target)
{
	return g->cost[n] + sqrtf(path_dist2(g->pos[n], g->pos[target]));
}

static void path_heap_put(MohaaPaths *g, int at, int n)
{
	g->heap[at] = (unsigned short)n;
	g->slot[n] = (unsigned short)at;
}

static void path_heap_up(MohaaPaths *g, int at, int target)
{
	const int n = g->heap[at];
	const float key = path_heap_key(g, n, target);
	while (at > 0 && path_heap_key(g, g->heap[(at - 1) / 2], target) > key) {
		path_heap_put(g, at, g->heap[(at - 1) / 2]);
		at = (at - 1) / 2;
	}
	path_heap_put(g, at, n);
}

static void path_heap_down(MohaaPaths *g, int size, int target)
{
	int at = 0;
	const int n = g->heap[0];
	const float key = path_heap_key(g, n, target);
	for (;;) {
		int c = at * 2 + 1;
		if (c >= size)
			break;
		if (c + 1 < size && path_heap_key(g, g->heap[c + 1], target) < path_heap_key(g, g->heap[c], target))
			c++;
		if (path_heap_key(g, g->heap[c], target) >= key)
			break;
		path_heap_put(g, at, g->heap[c]);
		at = c;
	}
	path_heap_put(g, at, n);
}

#define PATH_CLOSED 0xFFFE

static int MohaaPaths_NextHop(MohaaPaths *g, int from, int to, MohaaPathEdgeBlocked blocked, void *ctx)
{
	int size = 0, i;
	if (from < 0 || to < 0 || from >= g->count || to >= g->count)
		return -1;
	if (from == to)
		return to;
	/* searched from the goal back to the walker: each node's from[] is then its next step toward the goal */
	for (i = 0; i < g->count; i++)
		g->slot[i] = MOHAA_PATH_NONE;	/* unseen */
	g->cost[to] = 0.0f;
	g->from[to] = MOHAA_PATH_NONE;
	path_heap_put(g, size++, to);
	while (size > 0) {
		const int n = g->heap[0];
		g->slot[n] = PATH_CLOSED;
		if (n == from)
			return g->from[from];
		if (--size > 0) {
			path_heap_put(g, 0, g->heap[size]);
			path_heap_down(g, size, from);
		}
		for (i = 0; i < MOHAA_PATH_LINKS && g->link[n][i] != MOHAA_PATH_NONE; i++) {
			const int m = g->link[n][i];
			const float c = g->cost[n] + sqrtf(path_dist2(g->pos[n], g->pos[m]));
			if (blocked && blocked(ctx, g->pos[n], g->pos[m]))
				continue;
			if (g->slot[m] == PATH_CLOSED)
				continue;
			if (g->slot[m] == MOHAA_PATH_NONE) {
				g->cost[m] = c;
				g->from[m] = (unsigned short)n;
				path_heap_put(g, size, m);
				path_heap_up(g, size++, from);
			} else if (c < g->cost[m]) {
				g->cost[m] = c;
				g->from[m] = (unsigned short)n;
				path_heap_up(g, g->slot[m], from);
			}
		}
	}
	return -1;
}

#endif
