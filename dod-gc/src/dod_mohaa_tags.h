/* dod_mohaa_tags.h - baked MOHAA model tags and animation lengths, included once by dod_mohaa.c (all static).
 *
 * MOHAA's in-game cutscenes read tags of animated models every frame (m1l1's opening ride takes the truck, the
 * squad and the player's camera from vehicles/gmctruckpath_opening.tik) and wait for animations to end
 * ("waittill animdone"). There is no skeletal animation on the GameCube side, so mohaa-gc tools/mohaa_tags.py
 * bakes what a level's scripts ask for into maps/<map>.tags (layout in that tool's docstring): per model, the
 * frames of the tags the scripts name, and the length of every animation name the scripts mention.
 *
 * Everything lands in one block: names as hashes, frames as native int16 (the file is little-endian, the
 * GameCube is not). m1l1's file is about 50 KB. */
#ifndef MOHAA_TAGS_H
#define MOHAA_TAGS_H

#include <math.h>
#include <stdint.h>
#include <string.h>

typedef struct MohaaTagAnim {
	uint32_t name;
	float frametime, step;		/* seconds per frame; MOHAA units per position step */
	int frames;
	const int16_t *data;		/* frames x tags x (pos[3], quat[4]) */
} MohaaTagAnim;

typedef struct MohaaTagModel {
	uint32_t name;			/* hash of the path under models/, e.g. "vehicles/gmctruckpath_opening.tik" */
	int ntags, nanims;
	const uint32_t *tags;
	const MohaaTagAnim *anims;
} MohaaTagModel;

typedef struct MohaaTags {
	int ndur;
	const uint32_t *dur_name;
	const float *dur_secs;
	int nmodels;
	const MohaaTagModel *models;
	void *block;
	size_t size;
} MohaaTags;

/* FNV-1a of the lowercased name, with '\\' as '/' and a leading "models/" dropped (scripts write both) */
static uint32_t MohaaTags_Hash(const char *s)
{
	uint32_t h = 2166136261u;
	if (!s)
		return 0;
	if (!strncmp(s, "models/", 7) || !strncmp(s, "MODELS/", 7))
		s += 7;
	for (; *s; s++) {
		unsigned char c = (unsigned char)*s;
		if (c >= 'A' && c <= 'Z')
			c = (unsigned char)(c - 'A' + 'a');
		if (c == '\\')
			c = '/';
		h = (h ^ c) * 16777619u;
	}
	return h ? h : 1;
}

typedef struct MohaaTagsReader {
	const unsigned char *p, *end;
	int bad;
} MohaaTagsReader;

static uint32_t mtr_u32(MohaaTagsReader *r)
{
	uint32_t v;
	if (r->end - r->p < 4) { r->bad = 1; return 0; }
	v = (uint32_t)r->p[0] | ((uint32_t)r->p[1] << 8) | ((uint32_t)r->p[2] << 16) | ((uint32_t)r->p[3] << 24);
	r->p += 4;
	return v;
}
static unsigned mtr_u16(MohaaTagsReader *r)
{
	unsigned v;
	if (r->end - r->p < 2) { r->bad = 1; return 0; }
	v = (unsigned)r->p[0] | ((unsigned)r->p[1] << 8);
	r->p += 2;
	return v;
}
static unsigned mtr_u8(MohaaTagsReader *r)
{
	if (r->p >= r->end) { r->bad = 1; return 0; }
	return *r->p++;
}
static float mtr_f32(MohaaTagsReader *r)
{
	uint32_t u = mtr_u32(r);
	float f;
	memcpy(&f, &u, 4);
	return f;
}
static uint32_t mtr_name(MohaaTagsReader *r)
{
	char buf[256];
	unsigned n = mtr_u8(r);
	if ((unsigned)(r->end - r->p) < n) { r->bad = 1; return 0; }
	memcpy(buf, r->p, n);
	buf[n] = 0;
	r->p += n;
	return MohaaTags_Hash(buf);
}

#define MTAG_ALIGN(n) (((n) + 7u) & ~(size_t)7u)

/* One pass over the file: count (out NULL) or fill. Returns bytes needed, 0 when the file is bad. */
static size_t mohaa_tags_pass(const unsigned char *data, size_t len, MohaaTags *out, unsigned char *block)
{
	MohaaTagsReader r;
	size_t need = 0, at;
	uint32_t i, nd, nm;
	uint32_t *dn = NULL;
	float *ds = NULL;
	MohaaTagModel *models = NULL;
	r.p = data; r.end = data + len; r.bad = 0;
	if (len < 16 || memcmp(data, "MTAG", 4))
		return 0;
	r.p += 4;
	if (mtr_u32(&r) != 1)
		return 0;
	nd = mtr_u32(&r);
	if (r.bad || nd > 65536)
		return 0;
	need += MTAG_ALIGN(nd * sizeof(uint32_t)) + MTAG_ALIGN(nd * sizeof(float));
	if (block) {
		dn = (uint32_t *)block;
		ds = (float *)(block + MTAG_ALIGN(nd * sizeof(uint32_t)));
	}
	for (i = 0; i < nd; i++) {
		uint32_t h = mtr_name(&r);
		float s = mtr_f32(&r);
		if (block) { dn[i] = h; ds[i] = s; }
	}
	nm = mtr_u32(&r);
	if (r.bad || nm > 1024)
		return 0;
	at = need;
	need += MTAG_ALIGN(nm * sizeof(MohaaTagModel));
	if (block)
		models = (MohaaTagModel *)(block + at);
	for (i = 0; i < nm; i++) {
		uint32_t name = mtr_name(&r), *tags = NULL;
		unsigned nt = mtr_u8(&r), na, t, a;
		MohaaTagAnim *anims = NULL;
		if (block)
			tags = (uint32_t *)(block + need);
		need += MTAG_ALIGN(nt * sizeof(uint32_t));
		for (t = 0; t < nt; t++) {
			uint32_t h = mtr_name(&r);
			if (block) tags[t] = h;
		}
		na = mtr_u8(&r);
		if (block)
			anims = (MohaaTagAnim *)(block + need);
		need += MTAG_ALIGN(na * sizeof(MohaaTagAnim));
		for (a = 0; a < na; a++) {
			uint32_t aname = mtr_name(&r);
			float ft = mtr_f32(&r);
			unsigned nf = mtr_u16(&r);
			float step = mtr_f32(&r);
			size_t count = (size_t)nf * nt * 7, k;
			int16_t *d = block ? (int16_t *)(block + need) : NULL;
			if (r.bad || (size_t)(r.end - r.p) < count * 2)
				return 0;
			for (k = 0; k < count; k++) {
				uint16_t u = (uint16_t)(r.p[2 * k] | (r.p[2 * k + 1] << 8));
				if (d) d[k] = (int16_t)u;
			}
			r.p += count * 2;
			if (block) {
				anims[a].name = aname;
				anims[a].frametime = ft > 0.0f ? ft : 0.05f;
				anims[a].step = step;
				anims[a].frames = (int)nf;
				anims[a].data = d;
			}
			need += MTAG_ALIGN(count * sizeof(int16_t));
		}
		if (block) {
			models[i].name = name;
			models[i].ntags = (int)nt;
			models[i].nanims = (int)na;
			models[i].tags = tags;
			models[i].anims = anims;
		}
	}
	if (r.bad)
		return 0;
	if (out) {
		out->ndur = (int)nd;
		out->dur_name = dn;
		out->dur_secs = ds;
		out->nmodels = (int)nm;
		out->models = models;
	}
	return need ? need : 8;
}

typedef void *(*MohaaTagsAlloc)(void *ptr, size_t old_size, size_t new_size);

/* Parse a .tags file into one block from alloc. Returns 1 on success (tags then owns tags->block). */
static int MohaaTags_Load(MohaaTags *tags, const void *data, size_t len, MohaaTagsAlloc alloc)
{
	size_t need = mohaa_tags_pass((const unsigned char *)data, len, NULL, NULL);
	unsigned char *block;
	memset(tags, 0, sizeof(*tags));
	if (!need)
		return 0;
	block = (unsigned char *)alloc(NULL, 0, need);
	if (!block)
		return 0;
	memset(block, 0, need);
	mohaa_tags_pass((const unsigned char *)data, len, tags, block);
	tags->block = block;
	tags->size = need;
	return 1;
}

static void MohaaTags_Free(MohaaTags *tags, MohaaTagsAlloc alloc)
{
	if (tags->block && alloc)
		alloc(tags->block, tags->size, 0);
	memset(tags, 0, sizeof(*tags));
}

static int MohaaTags_Model(const MohaaTags *tags, uint32_t name)
{
	int i;
	for (i = 0; i < tags->nmodels; i++)
		if (tags->models[i].name == name)
			return i;
	return -1;
}

static int MohaaTags_Anim(const MohaaTagModel *m, uint32_t name)
{
	int i;
	for (i = 0; i < m->nanims; i++)
		if (m->anims[i].name == name)
			return i;
	return -1;
}

static int MohaaTags_Tag(const MohaaTagModel *m, uint32_t name)
{
	int i;
	for (i = 0; i < m->ntags; i++)
		if (m->tags[i] == name)
			return i;
	return -1;
}

/* Seconds the named animation plays: the model's own baked one first, else the level's length table; -1 unknown */
static float MohaaTags_Length(const MohaaTags *tags, int model, uint32_t anim)
{
	int i;
	if (model >= 0 && model < tags->nmodels) {
		const MohaaTagModel *m = &tags->models[model];
		i = MohaaTags_Anim(m, anim);
		if (i >= 0)
			return m->anims[i].frames * m->anims[i].frametime;
	}
	for (i = 0; i < tags->ndur; i++)
		if (tags->dur_name[i] == anim)
			return tags->dur_secs[i];
	return -1.0f;
}

/* A tag at t seconds into an animation, held at the last frame after the end: model-space position (MOHAA units)
 * and rotation as a textbook quaternion (x y z w), frames blended. */
static void MohaaTags_Sample(const MohaaTagModel *m, int anim, int tag, float t, float pos[3], float q[4])
{
	const MohaaTagAnim *a = &m->anims[anim];
	float f = t / a->frametime, w, dot = 0.0f, n = 0.0f;
	int f0, f1, k;
	const int16_t *p0, *p1;
	if (f < 0.0f)
		f = 0.0f;
	f0 = (int)f;
	if (f0 >= a->frames - 1) {
		f0 = f1 = a->frames - 1;
		w = 0.0f;
	} else {
		f1 = f0 + 1;
		w = f - (float)f0;
	}
	p0 = a->data + ((size_t)f0 * m->ntags + tag) * 7;
	p1 = a->data + ((size_t)f1 * m->ntags + tag) * 7;
	for (k = 0; k < 3; k++)
		pos[k] = (p0[k] + (p1[k] - p0[k]) * w) * a->step;
	for (k = 0; k < 4; k++)
		dot += (float)p0[3 + k] * (float)p1[3 + k];
	for (k = 0; k < 4; k++) {
		const float b = dot < 0.0f ? -(float)p1[3 + k] : (float)p1[3 + k];
		q[k] = (float)p0[3 + k] + (b - (float)p0[3 + k]) * w;
		n += q[k] * q[k];
	}
	n = n > 0.0f ? 1.0f / sqrtf(n) : 0.0f;
	for (k = 0; k < 4; k++)
		q[k] *= n;
	if (n == 0.0f)
		q[3] = 1.0f;
}

/* columns of the rotation: m[r][c], column 0 forward, 1 left, 2 up */
static void MohaaTags_QuatMatrix(const float q[4], float m[3][3])
{
	const float x = q[0], y = q[1], z = q[2], w = q[3];
	m[0][0] = 1 - 2 * (y * y + z * z); m[0][1] = 2 * (x * y - z * w);     m[0][2] = 2 * (x * z + y * w);
	m[1][0] = 2 * (x * y + z * w);     m[1][1] = 1 - 2 * (x * x + z * z); m[1][2] = 2 * (y * z - x * w);
	m[2][0] = 2 * (x * z - y * w);     m[2][1] = 2 * (y * z + x * w);     m[2][2] = 1 - 2 * (x * x + y * y);
}

/* MOHAA angles (pitch yaw roll, degrees; positive pitch looks down) as an axis matrix, columns forward left up */
static void MohaaTags_AnglesMatrix(const float a[3], float m[3][3])
{
	const float d = 3.14159265f / 180.0f;
	const float sp = sinf(a[0] * d), cp = cosf(a[0] * d), sy = sinf(a[1] * d), cy = cosf(a[1] * d);
	const float sr = sinf(a[2] * d), cr = cosf(a[2] * d);
	m[0][0] = cp * cy; m[1][0] = cp * sy; m[2][0] = -sp;
	m[0][1] = sr * sp * cy - cr * sy; m[1][1] = sr * sp * sy + cr * cy; m[2][1] = sr * cp;	/* left = -right */
	m[0][2] = cr * sp * cy + sr * sy; m[1][2] = cr * sp * sy - sr * cy; m[2][2] = cr * cp;
}

static void MohaaTags_MatrixAngles(const float m[3][3], float a[3])
{
	const float r = 180.0f / 3.14159265f;
	float s = -m[2][0];
	if (s > 1.0f) s = 1.0f;
	if (s < -1.0f) s = -1.0f;
	a[0] = asinf(s) * r;
	a[1] = atan2f(m[1][0], m[0][0]) * r;
	a[2] = atan2f(m[2][1], m[2][2]) * r;
}

#endif
