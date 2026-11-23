/* dod_mohaa.c - bind MOHAA script commands to GoldSrc entities. See dod_mohaa.h. */
#include "dod_mohaa.h"

#include "morpheus.h"
#include "dod_mohaa_paths.h"
#include "dod_mohaa_pool.h"
#include "dod_mohaa_tags.h"

static MohaaPool g_pool;  /* used when the backend gives a region (DodMohaaBackend.pool) */

static void *default_alloc(void *ptr, size_t old_size, size_t new_size)
{
	(void)old_size;
	if (!new_size) {
		free(ptr);
		return NULL;
	}
	return realloc(ptr, new_size);
}

/* Blocks the pool cannot fit go to the heap, each behind a link so that dropping the pool can free them.
   The link is two pointers, a multiple of 8 bytes, so the block after it keeps malloc's alignment. */
typedef struct HeapLink {
	struct HeapLink *prev, *next;
} HeapLink;
static HeapLink *g_heap;   /* overflow blocks, newest first */
static size_t g_heap_used;

static int pool_owns(const void *ptr)
{
	const unsigned char *q = (const unsigned char *)ptr;
	int r;
	for (r = 0; r < g_pool.nregions; r++)
		if (q >= g_pool.rbase[r] && q < g_pool.rbase[r] + g_pool.rsize[r])
			return 1;
	return 0;
}

static void heap_unlink(HeapLink *h)
{
	if (h->prev)
		h->prev->next = h->next;
	else
		g_heap = h->next;
	if (h->next)
		h->next->prev = h->prev;
}

static void heap_link(HeapLink *h)
{
	h->prev = NULL;
	h->next = g_heap;
	if (g_heap)
		g_heap->prev = h;
	g_heap = h;
}

static void *heap_get(size_t n)
{
	HeapLink *h;
	if (n > (size_t)-1 - sizeof(HeapLink))
		return NULL;
	h = (HeapLink *)malloc(sizeof(HeapLink) + n);
	if (!h)
		return NULL;
	heap_link(h);
	g_heap_used += n;
	return h + 1;
}

static void heap_put(void *ptr, size_t old_size)
{
	HeapLink *h = (HeapLink *)ptr - 1;
	heap_unlink(h);
	g_heap_used -= old_size;
	free(h);
}

/* free every overflow block: the VM that owned them is gone */
static void heap_drop(void)
{
	while (g_heap) {
		HeapLink *h = g_heap;
		g_heap = h->next;
		free(h);
	}
	g_heap_used = 0;
}

static void *pool_alloc(void *ptr, size_t old_size, size_t new_size)
{
	void *q;
	if (!ptr) {
		q = MohaaPool_Alloc(&g_pool, new_size);
		return q ? q : (new_size ? heap_get(new_size) : NULL);
	}
	if (pool_owns(ptr)) {
		if (!new_size) {
			MohaaPool_Free(&g_pool, ptr);
			return NULL;
		}
		q = MohaaPool_Realloc(&g_pool, ptr, new_size);
		if (q)
			return q;
		q = heap_get(new_size);   /* the pool is full: move the block out */
		if (!q)
			return NULL;
		memcpy(q, ptr, old_size < new_size ? old_size : new_size);
		MohaaPool_Free(&g_pool, ptr);
		return q;
	}
	if (!new_size) {
		heap_put(ptr, old_size);
		return NULL;
	}
	q = MohaaPool_Alloc(&g_pool, new_size);   /* back into the pool when it has room again */
	if (!q) {
		HeapLink *h = (HeapLink *)ptr - 1, *g;
		if (new_size > (size_t)-1 - sizeof(HeapLink))
			return NULL;
		heap_unlink(h);
		g = (HeapLink *)realloc(h, sizeof(HeapLink) + new_size);
		if (!g) {
			heap_link(h);
			return NULL;
		}
		heap_link(g);
		g_heap_used += new_size;
		g_heap_used -= old_size;
		return g + 1;
	}
	memcpy(q, ptr, old_size < new_size ? old_size : new_size);
	heap_put(ptr, old_size);
	return q;
}

/* compiler scratch goes to the top of the pool (see dod_mohaa_pool.h) */
static void h_scratch(void *user, int on)
{
	(void)user;
	MohaaPool_Top(&g_pool, on);
}

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct DodMover {
	uint32_t id;
	float time;              /* "$obj time 2" */
	int has_dest, has_angles;
	float dest[3];           /* GoldSrc units */
	float angles[3];
	float spin[3];           /* rotatex/y/z, degrees per second, kept across moves */
	int moving;
	float end_time;
	/* "drive $path speed": the node it heads for now, along the path's target chain */
	uint32_t drive_node;
	float drive_speed;       /* GoldSrc units per second */
	int driving;
} DodMover;

#define MAX_UNKNOWN 128
#define MAX_LOOPS 16
#define MAX_SOUND_MISSES 64
#define MAX_MOODS 8
#define DOD_MOHAA_MAX_ROUTES 48	/* one per grunt slot */
#define MUSIC_PATH 80
#define DOD_MOHAA_MAX_CINE 64
#define DOD_MOHAA_ANIM_DEFAULT 1.0f	/* seconds an animation with no baked length plays before "animdone" */

/* An entity a cutscene drives: its MOHAA model and animation (for tags and animdone), what it is glued to, where an
   actor aims, a turret's view. */
typedef struct DodCine {
	uint32_t id;
	int model;               /* index in S.tags, -1 none */
	uint32_t anim;           /* hash of the animation playing, 0 none */
	float anim_start, anim_end;
	int done_pending;        /* "animdone" not yet sent */
	uint32_t glue;           /* follows this entity */
	int glue_angles;
	int has_aim;
	uint32_t aim_id;
	float aim[3];            /* GoldSrc units, when aim_id is 0 */
	int has_view;
	float view[3];           /* "viewangles" a script set (a turret the player rides) */
} DodCine;

typedef struct DodSound {
	uint32_t hash;           /* of the alias, lowercase */
	uint16_t alias, sample;  /* offsets into the text block */
	float volume, attn;
	uint8_t channel;
} DodSound;

static struct {
	DodMohaaBackend be;
	ms_vm *vm;
	int ticks;
	float now;
	DodMover movers[DOD_MOHAA_MAX_MOVERS];
	const char *unknown[MAX_UNKNOWN];
	int nunknown;
	DodSound *sounds;        /* one block: rows, then their strings */
	size_t sounds_size;
	int nsounds;
	const char *sound_text;
	struct { uint32_t id; const char *sample; } loops[MAX_LOOPS];
	uint32_t sound_misses[MAX_SOUND_MISSES];
	int nmisses;
	uint32_t rng;
	/* music: the soundtrack's moods (music/<name>.mood), the mood playing, a triggered cue over it */
	struct { char name[8]; char sample[MUSIC_PATH]; uint8_t loop; } moods[MAX_MOODS];
	int nmoods, mood, fallback;
	char cue[MUSIC_PATH];
	int cue_loop;
	char level_script[128];
	int started;              /* main has run (it waits for the first frame: entities spawn after the VM) */
	size_t budget;
	char objectives[8][96];	/* addobjective texts, by index 1..8 */	/* maps/<map>.scr, where a trigger's setthread label lives */
	/* path nodes, and the soldiers walking them: a route is the goal plus the node it heads for now */
	MohaaPaths paths;
	int path_links;
	struct { uint32_t id; int order; float goal[3]; unsigned short node, goal_node; } routes[DOD_MOHAA_MAX_ROUTES];
	/* cutscenes: maps/<map>.tags, the entities they drive, the player's state */
	MohaaTags tags;
	DodCine cine[DOD_MOHAA_MAX_CINE];
	uint32_t player;          /* the player a cutscene holds (locked, glued or riding), 0 none */
	int player_locked;
	uint32_t ride;            /* the turret the player rides ("doUse $player"): their eyes follow it */
	int ride_fresh;           /* the ride just began: set the view, then follow its turns */
	float ride_yaw;
	int drawhud_off;          /* "drawhud 0" */
	int hud_sent;             /* DOD_MOHAA_HUD_* bits last given to the backend, -1 none yet */
} S;

static DodCine *cine(uint32_t id, int create);
static int is_player(uint32_t id);

/* ------------------------------------------------------------------ */
/* helpers                                                              */
/* ------------------------------------------------------------------ */

static void scale_in(const float in[3], float out[3])
{
	out[0] = in[0] * DOD_MOHAA_SCALE;
	out[1] = in[1] * DOD_MOHAA_SCALE;
	out[2] = in[2] * DOD_MOHAA_SCALE;
}

static void scale_out(const float in[3], float out[3])
{
	out[0] = in[0] / DOD_MOHAA_SCALE;
	out[1] = in[1] / DOD_MOHAA_SCALE;
	out[2] = in[2] / DOD_MOHAA_SCALE;
}

static uint32_t target_id(ms_call *c)
{
	return ms_call_target(c)->u.id;
}

static DodMover *mover(uint32_t id, int create)
{
	int i, free_slot = -1;
	for (i = 0; i < DOD_MOHAA_MAX_MOVERS; i++) {
		if (S.movers[i].id == id)
			return &S.movers[i];
		if (!S.movers[i].id && free_slot < 0)
			free_slot = i;
	}
	if (!create || free_slot < 0)
		return NULL;
	memset(&S.movers[free_slot], 0, sizeof(DodMover));
	S.movers[free_slot].id = id;
	S.movers[free_slot].time = 1.0f;   /* MOHAA's default move time */
	return &S.movers[free_slot];
}

static void forget(uint32_t id)
{
	DodMover *m = mover(id, 0);
	int i;
	if (m)
		memset(m, 0, sizeof(*m));
	for (i = 0; i < MAX_LOOPS; i++)
		if (S.loops[i].id == id)
			S.loops[i].id = 0;   /* the engine stops an entity's sounds when it goes */
	for (i = 0; i < DOD_MOHAA_MAX_ROUTES; i++)
		if (S.routes[i].id == id)
			S.routes[i].id = 0;
	for (i = 0; i < DOD_MOHAA_MAX_CINE; i++)
		if (S.cine[i].id == id)
			memset(&S.cine[i], 0, sizeof(S.cine[i]));
	if (S.ride == id)
		S.ride = 0;
}

/* destination argument: a vector in MOHAA units, or an entity to move onto */
/* ---- path nodes seen as entities (DOD_MOHAA_NODE_ID) ---- */
static int is_node(uint32_t id)
{
	return (id & DOD_MOHAA_NODE_ID) != 0;
}

static int valid(uint32_t id)
{
	if (is_node(id))
		return (int)(id & ~DOD_MOHAA_NODE_ID) < S.paths.count;
	return S.be.valid(id);
}

static void get_vec(uint32_t id, int what, float out[3])
{
	if (!is_node(id)) {
		S.be.get_vec(id, what, out);
		return;
	}
	const int k = (int)(id & ~DOD_MOHAA_NODE_ID);
	out[0] = out[1] = out[2] = 0.0f;
	if (what == DOD_MOHAA_ORIGIN && k < S.paths.count)
		memcpy(out, S.paths.pos[k], sizeof(float) * 3);
}

static int node_origin(const char *name, float out[3])
{
	const int k = MohaaPaths_Find(&S.paths, name);
	if (k < 0)
		return 0;
	memcpy(out, S.paths.pos[k], sizeof(float) * 3);
	return 1;
}

static int dest_arg(ms_call *c, int i, float out[3])
{
	const ms_value *v = ms_arg(c, i);
	if (v->type == MS_ENTITY) {
		if (!valid(v->u.id))
			return 0;
		get_vec(v->u.id, DOD_MOHAA_ORIGIN, out);
		return 1;
	}
	if (v->type != MS_VECTOR && v->type != MS_STRING)
		return 0;
	if (v->type == MS_STRING) {
		/* "$node" or "node": a targetname (MOHAA path nodes are often passed by name) */
		const char *name = ms_arg_string(c, i);
		if (name[0] == '$')
			name++;
		if ((name[0] >= 'a' && name[0] <= 'z') || (name[0] >= 'A' && name[0] <= 'Z') || name[0] == '_') {
			uint32_t id = 0;
			if (S.be.find(name, &id, 1) < 1 || !id || !valid(id))
				return node_origin(name, out);
			get_vec(id, DOD_MOHAA_ORIGIN, out);
			return 1;
		}
	}
	{
		float raw[3];
		ms_arg_vector(c, i, raw);
		scale_in(raw, out);
	}
	return 1;
}

/* ------------------------------------------------------------------ */
/* host callbacks                                                       */
/* ------------------------------------------------------------------ */

static void *h_alloc(void *user, void *ptr, size_t old_size, size_t new_size)
{
	(void)user;
	return S.be.alloc(ptr, old_size, new_size);
}

static char *h_load(void *user, const char *path, size_t *len)
{
	char *text;
	(void)user;
	text = S.be.load_file(path, len);
	if (!text && S.vm) {
		/* missing, or the engine had no room for the text: say how much the scripts hold, to tell which */
		char msg[192];
		snprintf(msg, sizeof(msg), "mohaa: could not load %s (scripts hold %u KB, peak %u KB)\n", path,
			(unsigned)(ms_memory_used(S.vm) / 1024u), (unsigned)(ms_memory_peak(S.vm) / 1024u));
		S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
	}
	return text;
}

static void h_free(void *user, char *text)
{
	(void)user;
	if (S.be.free_file)
		S.be.free_file(text);
}

static void h_print(void *user, int channel, const char *text)
{
	(void)user;
	switch (channel) {
	case MS_PRINT_HUD:
	case MS_PRINT_HUD_BOLD: S.be.print(DOD_MOHAA_PRINT_HUD, text); break;
	case MS_PRINT_ERROR:
		S.be.print(DOD_MOHAA_PRINT_ERROR, text);
		if (S.vm && strstr(text, "out of memory")) {
			/* the VM's budget ran out (mohaa_script_kb): say how full it was, to size the budget */
			char msg[160];
			snprintf(msg, sizeof(msg), "mohaa: script memory %u KB in use, peak %u KB, budget %u KB\n",
				(unsigned)(ms_memory_used(S.vm) / 1024u), (unsigned)(ms_memory_peak(S.vm) / 1024u),
				(unsigned)(S.budget / 1024u));
			S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
			if (S.be.alloc == pool_alloc) {
				snprintf(msg, sizeof(msg), "mohaa: script pool %u of %u KB used, largest free piece %u KB\n",
					(unsigned)(g_pool.used / 1024u), (unsigned)(g_pool.size / 1024u),
					(unsigned)(MohaaPool_Largest(&g_pool) / 1024u));
				S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
				snprintf(msg, sizeof(msg), "mohaa: %u KB more on the engine heap\n", (unsigned)(g_heap_used / 1024u));
				S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
			}
		}
		break;
	default: S.be.print(DOD_MOHAA_PRINT_CONSOLE, text); break;
	}
}

static int h_find(void *user, const char *name, uint32_t *ids, int max)
{
	int n;
	(void)user;
	n = S.be.find(name, ids, max);
	if (n == 0 && max > 0) {
		const int k = MohaaPaths_Find(&S.paths, name);
		if (k >= 0) {
			ids[0] = DOD_MOHAA_NODE_ID | (uint32_t)k;
			return 1;
		}
	}
	return n;
}

static int h_valid(void *user, uint32_t id)
{
	(void)user;
	return valid(id);
}

static int h_get_field(void *user, const ms_value *l, const char *name, ms_value *out)
{
	float v[3];
	(void)user;
	if (l->type != MS_ENTITY)
		return 0;
	if (!strcmp(name, "origin")) {
		get_vec(l->u.id, DOD_MOHAA_ORIGIN, v);
		scale_out(v, v);
		*out = ms_vec(v[0], v[1], v[2]);
		return 1;
	}
	if (!strcmp(name, "angles")) {
		get_vec(l->u.id, DOD_MOHAA_ANGLES, v);
		*out = ms_vec(v[0], v[1], v[2]);
		return 1;
	}
	if (!strcmp(name, "forwardvector") || !strcmp(name, "leftvector") || !strcmp(name, "rightvector") ||
	    !strcmp(name, "upvector")) {
		/* unit axes from angles (pitch yaw roll, degrees; positive pitch looks down), as AngleVectors */
		const float d = 3.14159265f / 180.0f;
		float sp, cp, sy, cy, sr, cr, f[3];
		get_vec(l->u.id, DOD_MOHAA_ANGLES, v);
		sp = sinf(v[0] * d); cp = cosf(v[0] * d);
		sy = sinf(v[1] * d); cy = cosf(v[1] * d);
		sr = sinf(v[2] * d); cr = cosf(v[2] * d);
		if (name[0] == 'f') {
			f[0] = cp * cy; f[1] = cp * sy; f[2] = -sp;
		} else if (name[0] == 'u') {
			f[0] = cr * sp * cy + sr * sy; f[1] = cr * sp * sy - sr * cy; f[2] = cr * cp;
		} else {   /* right; left is its negation */
			const float k = name[0] == 'l' ? -1.0f : 1.0f;
			f[0] = k * (-sr * sp * cy + cr * sy); f[1] = k * (-sr * sp * sy - cr * cy); f[2] = k * (-sr * cp);
		}
		*out = ms_vec(f[0], f[1], f[2]);
		return 1;
	}
	if (!strcmp(name, "health")) {
		*out = ms_float(S.be.get_health(l->u.id));
		return 1;
	}
	if (!strcmp(name, "viewangles")) {
		const DodCine *k = cine(l->u.id, 0);
		if (k && k->has_view)
			*out = ms_vec(k->view[0], k->view[1], k->view[2]);
		else {
			get_vec(l->u.id, DOD_MOHAA_ANGLES, v);
			*out = ms_vec(v[0], v[1], v[2]);
		}
		return 1;
	}
	if (!strcmp(name, "targetname") || !strcmp(name, "classname") || !strcmp(name, "model")) {
		int what = name[0] == 't' ? DOD_MOHAA_TARGETNAME : name[0] == 'c' ? DOD_MOHAA_CLASSNAME : DOD_MOHAA_MODEL;
		const char *s = S.be.get_str(l->u.id, what);
		*out = ms_string(S.vm, s ? s : "");
		return 1;
	}
	if (!strcmp(name, "target")) {
		/* the map's target; with none, a target the script set itself (an entity var) */
		const char *s = S.be.get_str(l->u.id, DOD_MOHAA_TARGET);
		if (!s || !*s)
			return 0;
		*out = ms_string(S.vm, s);
		return 1;
	}
	return 0;
}

static int h_set_field(void *user, const ms_value *l, const char *name, const ms_value *val)
{
	float v[3];
	(void)user;
	if (l->type != MS_ENTITY)
		return 0;
	if (!strcmp(name, "origin") && val->type == MS_VECTOR) {
		scale_in(val->u.v, v);
		S.be.set_vec(l->u.id, DOD_MOHAA_ORIGIN, v);
		return 1;
	}
	if (!strcmp(name, "angles") && val->type == MS_VECTOR) {
		S.be.set_vec(l->u.id, DOD_MOHAA_ANGLES, val->u.v);
		return 1;
	}
	if (!strcmp(name, "health")) {
		S.be.set_health(l->u.id, ms_to_float(val));
		return 1;
	}
	if (!strcmp(name, "viewangles") && val->type == MS_VECTOR) {
		/* a turret's view (the player riding it turns with it, see cine_think); the player's own view */
		DodCine *k = cine(l->u.id, 1);
		if (is_player(l->u.id) && S.be.view)
			S.be.view(l->u.id, val->u.v, 0);
		if (k) {
			memcpy(k->view, val->u.v, sizeof(k->view));
			k->has_view = 1;
		}
		return 1;
	}
	if (!strcmp(name, "targetname")) {
		char buf[96];
		S.be.set_targetname(l->u.id, ms_tostring(val, buf, sizeof(buf)));
		return 1;
	}
	return 0;
}

/* Commands nobody binds yet are reported once each and otherwise ignored, so a
 * half-bound mission keeps running and the console lists what is missing. */
static int h_unknown(ms_call *c)
{
	const char *name = ms_call_name(c);
	int i;
	for (i = 0; i < S.nunknown; i++)
		if (S.unknown[i] == name)
			return 1;
	if (S.nunknown < MAX_UNKNOWN) {
		char msg[160];
		S.unknown[S.nunknown++] = name;   /* interned by the VM, stable while it lives */
		snprintf(msg, sizeof(msg), "mohaa: '%s' on %s is not bound yet\n", name, ms_type_name(ms_call_target(c)->type));
		S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
	}
	return 1;
}

/* ------------------------------------------------------------------ */
/* entity commands                                                      */
/* ------------------------------------------------------------------ */

static int c_hide(ms_call *c) { S.be.set_flag(target_id(c), DOD_MOHAA_HIDDEN, 1); return 0; }
static int c_show(ms_call *c) { S.be.set_flag(target_id(c), DOD_MOHAA_HIDDEN, 0); return 0; }
static int c_notsolid(ms_call *c) { S.be.set_flag(target_id(c), DOD_MOHAA_NOTSOLID, 1); return 0; }
static int c_solid(ms_call *c) { S.be.set_flag(target_id(c), DOD_MOHAA_NOTSOLID, 0); return 0; }

static int c_remove(ms_call *c)
{
	uint32_t id = target_id(c);
	forget(id);
	S.be.remove(id);
	ms_entity_removed(S.vm, id);
	return 0;
}

static int c_origin(ms_call *c)
{
	float v[3];
	if (!dest_arg(c, 0, v))
		return ms_call_error(c, "needs a vector");
	S.be.set_vec(target_id(c), DOD_MOHAA_ORIGIN, v);
	return 0;
}

static int c_angles(ms_call *c)
{
	float v[3];
	ms_arg_vector(c, 0, v);
	S.be.set_vec(target_id(c), DOD_MOHAA_ANGLES, v);
	return 0;
}

static int c_health(ms_call *c)
{
	S.be.set_health(target_id(c), ms_arg_float(c, 0));
	return 0;
}

static int c_time(ms_call *c)
{
	DodMover *m = mover(target_id(c), 1);
	if (!m)
		return ms_call_error(c, "too many moving objects");
	m->time = ms_arg_float(c, 0);
	return 0;
}

static int c_moveto(ms_call *c)
{
	DodMover *m = mover(target_id(c), 1);
	if (!m)
		return ms_call_error(c, "too many moving objects");
	if (!dest_arg(c, 0, m->dest))
		return ms_call_error(c, "needs a vector or an entity");
	m->has_dest = 1;
	return 0;
}

/* moveUp 64, moveNorth 128 ...: offsets in MOHAA units from the pending destination */
static int c_move_dir(ms_call *c)
{
	const char *n = ms_call_name(c) + 4;   /* after "move" */
	DodMover *m = mover(target_id(c), 1);
	float d = ms_arg_float(c, 0) * DOD_MOHAA_SCALE;
	int axis = 0;
	if (!m)
		return ms_call_error(c, "too many moving objects");
	if (!m->has_dest) {
		get_vec(m->id, DOD_MOHAA_ORIGIN, m->dest);
		m->has_dest = 1;
	}
	if (!strcmp(n, "up")) axis = 2;
	else if (!strcmp(n, "down")) { axis = 2; d = -d; }
	else if (!strcmp(n, "north")) axis = 1;
	else if (!strcmp(n, "south")) { axis = 1; d = -d; }
	else if (!strcmp(n, "east")) axis = 0;
	else if (!strcmp(n, "west")) { axis = 0; d = -d; }
	m->dest[axis] += d;
	return 0;
}

static int c_rotateto(ms_call *c)
{
	DodMover *m = mover(target_id(c), 1);
	if (!m)
		return ms_call_error(c, "too many moving objects");
	ms_arg_vector(c, 0, m->angles);
	m->has_angles = 1;
	return 0;
}

/* rotateYup 90 / rotateXdown 45 ...: turn the pending angles by that much (on the next move / waitmove) */
static int c_rotate_rel(ms_call *c)
{
	const char *n = ms_call_name(c);   /* rotate[xyz](up|down) */
	DodMover *m = mover(target_id(c), 1);
	const int axis = n[6] == 'x' ? 0 : n[6] == 'y' ? 1 : 2;
	const float d = ms_arg_float(c, 0);
	if (!m)
		return ms_call_error(c, "too many moving objects");
	if (!m->has_angles) {
		get_vec(m->id, DOD_MOHAA_ANGLES, m->angles);
		m->has_angles = 1;
	}
	m->angles[axis] += n[7] == 'u' ? d : -d;
	return 0;
}

static void apply_spin(DodMover *m)
{
	static const float zero[3] = {0, 0, 0};
	S.be.set_velocity(m->id, zero, m->spin);
}

/* rotateX 90: spin at 90 degrees a second until told otherwise (0 stops) */
static int c_rotate_axis(ms_call *c)
{
	const char *n = ms_call_name(c);
	DodMover *m = mover(target_id(c), 1);
	if (!m)
		return ms_call_error(c, "too many moving objects");
	/* MOHAA x/y/z are pitch, yaw and roll in GoldSrc's angle order */
	m->spin[n[6] == 'x' ? 0 : n[6] == 'y' ? 1 : 2] = ms_arg_float(c, 0);
	if (!m->moving)
		apply_spin(m);
	return 0;
}

static void start_move(DodMover *m)
{
	float org[3], ang[3], vel[3] = {0, 0, 0}, avel[3];
	int i;
	get_vec(m->id, DOD_MOHAA_ORIGIN, org);
	get_vec(m->id, DOD_MOHAA_ANGLES, ang);
	if (m->time <= 0.0f) {
		if (m->has_dest)
			S.be.set_vec(m->id, DOD_MOHAA_ORIGIN, m->dest);
		if (m->has_angles)
			S.be.set_vec(m->id, DOD_MOHAA_ANGLES, m->angles);
		m->has_dest = m->has_angles = 0;
		m->moving = 0;
		m->end_time = S.now;
		return;
	}
	for (i = 0; i < 3; i++) {
		vel[i] = m->has_dest ? (m->dest[i] - org[i]) / m->time : 0.0f;
		avel[i] = m->has_angles ? (m->angles[i] - ang[i]) / m->time : m->spin[i];
	}
	S.be.set_velocity(m->id, vel, avel);
	m->moving = 1;
	m->end_time = S.now + m->time;
}

static int c_move(ms_call *c)
{
	DodMover *m = mover(target_id(c), 1);
	if (!m)
		return ms_call_error(c, "too many moving objects");
	start_move(m);
	return 0;
}

static int c_waitmove(ms_call *c)
{
	DodMover *m = mover(target_id(c), 1);
	if (!m)
		return ms_call_error(c, "too many moving objects");
	start_move(m);
	if (m->moving)
		ms_call_wait_signal(c, ms_call_target(c), "movedone");
	return 0;
}

/* ---- vehicles: "drive $path [speed]" moves the vehicle node to node along the path's target chain and says
   "drive" at the end; there is no vehicle physics or model yet, so it glides from node to node ---- */

static uint32_t next_node(uint32_t id)
{
	const char *t;
	uint32_t ids[1];
	if (!id || is_node(id) || !valid(id))
		return 0;
	t = S.be.get_str(id, DOD_MOHAA_TARGET);
	if (!t || !*t)
		return 0;
	return h_find(NULL, t, ids, 1) == 1 ? ids[0] : 0;
}

static void drive_leg(DodMover *m)
{
	float org[3], to[3], d = 0.0f;
	int i;
	if (!m->drive_node || !valid(m->drive_node)) {
		ms_value ent = ms_entity(m->id);
		m->driving = 0;
		m->drive_node = 0;
		ms_notify(S.vm, &ent, "drive");
		return;
	}
	get_vec(m->id, DOD_MOHAA_ORIGIN, org);
	get_vec(m->drive_node, DOD_MOHAA_ORIGIN, to);
	for (i = 0; i < 3; i++)
		d += (to[i] - org[i]) * (to[i] - org[i]);
	memcpy(m->dest, to, sizeof(to));
	m->has_dest = 1;
	m->time = sqrtf(d) / m->drive_speed;
	if (m->time < 0.05f)
		m->time = 0.05f;   /* one frame at least, so a path of nodes on one spot still ends */
	start_move(m);
}

static int c_drive(ms_call *c)
{
	const ms_value *v = ms_arg(c, 0);
	DodMover *m = mover(target_id(c), 1);
	float speed = ms_argc(c) > 1 ? ms_arg_float(c, 1) : 200.0f;
	if (!m)
		return ms_call_error(c, "too many moving objects");
	if (v->type != MS_ENTITY || !valid(v->u.id))
		return ms_call_error(c, "drive: no such path");
	m->drive_node = v->u.id;
	m->drive_speed = (speed > 0.0f ? speed : 200.0f) * DOD_MOHAA_SCALE;
	m->driving = 1;
	drive_leg(m);
	return 0;
}

/* "followpath $path": glide along a spline path's target chain (a looped chain goes round for good) */
static int c_followpath(ms_call *c)
{
	const ms_value *v = ms_arg(c, 0);
	DodMover *m = mover(target_id(c), 1);
	float speed = 100.0f;
	int i;
	if (!m)
		return ms_call_error(c, "too many moving objects");
	if (v->type != MS_ENTITY || !valid(v->u.id))
		return ms_call_error(c, "followpath: no such path");
	for (i = 1; i < ms_argc(c); i++)
		if (ms_arg(c, i)->type == MS_FLOAT || ms_arg(c, i)->type == MS_INT)
			speed = ms_arg_float(c, i);   /* the rest are flags ("loop" ...): the chain decides */
	m->drive_node = v->u.id;
	m->drive_speed = (speed > 0.0f ? speed : 100.0f) * DOD_MOHAA_SCALE;
	m->driving = 1;
	drive_leg(m);
	return 0;
}

/* "modifydrive speed ...": a new speed from the next node on */
static int c_modifydrive(ms_call *c)
{
	DodMover *m = mover(target_id(c), 0);
	const float speed = ms_arg_float(c, 0);
	if (m && m->driving && speed > 0.0f)
		m->drive_speed = speed * DOD_MOHAA_SCALE;
	return 0;
}

/* "stop" / "fullstop": stays where it is, and the drive is over without "drive" */
static int c_stopdrive(ms_call *c)
{
	static const float zero[3] = {0, 0, 0};
	DodMover *m = mover(target_id(c), 0);
	if (!m || !m->driving)
		return 0;
	m->driving = 0;
	m->drive_node = 0;
	m->moving = 0;
	m->has_dest = 0;
	S.be.set_velocity(m->id, zero, m->spin);
	return 0;
}

/* ---- actors (MOHAA AI soldiers; the game plays them with grunts) ---- */

/* say what the script sent the order to, so the cause shows in the log */
static int not_actor(ms_call *c, uint32_t id)
{
	const char *cls = id && valid(id) && !is_node(id) ? S.be.get_str(id, DOD_MOHAA_CLASSNAME) : NULL;
	const char *tn = id && valid(id) && !is_node(id) ? S.be.get_str(id, DOD_MOHAA_TARGETNAME) : NULL;
	return ms_call_error(c, "%s: not an actor (%s%s%s)", ms_call_name(c),
		!id || !valid(id) ? "no such entity" : is_node(id) ? "a path node" : cls && *cls ? cls : "?",
		tn && *tn ? " $" : "", tn && *tn ? tn : "");
}

static int actor_order(ms_call *c, int order, const float pos[3])
{
	static const float zero[3] = {0, 0, 0};
	if (!S.be.actor || !S.be.actor(target_id(c), order, pos ? pos : zero))
		return not_actor(c, target_id(c));
	return 0;
}

static int c_ai_on(ms_call *c) { return actor_order(c, DOD_MOHAA_AI_ON, NULL); }
static int c_ai_off(ms_call *c) { return actor_order(c, DOD_MOHAA_AI_OFF, NULL); }
static int c_attackplayer(ms_call *c) { return actor_order(c, DOD_MOHAA_ATTACK, NULL); }

/* ---- routes: a walk/run order over path nodes, one leg at a time; the grunt only ever walks straight ---- */

static int route_slot(uint32_t id, int make)
{
	int i, free_i = -1;
	for (i = 0; i < DOD_MOHAA_MAX_ROUTES; i++) {
		if (S.routes[i].id == id)
			return i;
		if (!S.routes[i].id && free_i < 0)
			free_i = i;
	}
	return make ? free_i : -1;
}

/* Plan id's walk to goal from its feet at from. Returns the first point to head for (a node, or the goal itself
   when nodes do not help) in leg, and the nodes the route uses (0 straight). */
static int route_plan(uint32_t id, int order, const float from[3], const float goal[3], float leg[3])
{
	int k = route_slot(id, 0), s, g, hops = 0, n;
	if (k >= 0)
		S.routes[k].id = 0;
	memcpy(leg, goal, sizeof(float) * 3);
	if (S.paths.count < 2 || !S.path_links)
		return 0;
	s = MohaaPaths_Nearest(&S.paths, from);
	g = MohaaPaths_Nearest(&S.paths, goal);
	{
		const float *sp = S.paths.pos[s];
		const float to_goal = (goal[0] - from[0]) * (goal[0] - from[0]) + (goal[1] - from[1]) * (goal[1] - from[1]);
		const float to_node = (sp[0] - from[0]) * (sp[0] - from[0]) + (sp[1] - from[1]) * (sp[1] - from[1]);
		/* nodes only when the goal is past the first node and the two ends are joined */
		if (s == g || to_goal <= to_node || MohaaPaths_NextHop(&S.paths, s, g) < 0)
			return 0;
	}
	k = route_slot(id, 1);
	if (k < 0)
		return 0;
	S.routes[k].id = id;
	S.routes[k].order = order;
	memcpy(S.routes[k].goal, goal, sizeof(float) * 3);
	S.routes[k].node = (unsigned short)s;
	S.routes[k].goal_node = (unsigned short)g;
	memcpy(leg, S.paths.pos[s], sizeof(float) * 3);
	for (n = s; n != g && hops < S.paths.count; hops++)
		n = MohaaPaths_NextHop(&S.paths, n, g);
	return hops + 1;
}

/* id reached the point it was sent to. Returns 1 when that was a node short of the goal (the next leg is ordered
   and the script does not hear "movedone"), 0 when the walk is over. */
static int route_arrived(uint32_t id)
{
	const int k = route_slot(id, 0);
	int h;
	if (k < 0)
		return 0;
	if (S.routes[k].node == S.routes[k].goal_node) {
		S.routes[k].id = 0;
		/* the last leg, from the goal's node onto the goal itself */
		if (S.be.actor)
			S.be.actor(id, S.routes[k].order, S.routes[k].goal);
		return 1;
	}
	h = MohaaPaths_NextHop(&S.paths, S.routes[k].node, S.routes[k].goal_node);
	if (h < 0) {
		S.routes[k].id = 0;
		if (S.be.actor)
			S.be.actor(id, S.routes[k].order, S.routes[k].goal);
		return 1;
	}
	S.routes[k].node = (unsigned short)h;
	if (S.be.actor)
		S.be.actor(id, S.routes[k].order, S.paths.pos[h]);
	return 1;
}

static int c_goto(ms_call *c)
{
	float pos[3], from[3], leg[3];
	const char *name = ms_call_name(c);
	const int order = (name[0] == 'r' || name[0] == 'R') ? DOD_MOHAA_RUNTO : DOD_MOHAA_WALKTO;
	const uint32_t id = target_id(c);
	int nodes;
	if (!dest_arg(c, 0, pos))
		return ms_call_error(c, "%s needs a vector, an entity or a node name", name);
	if (!S.be.actor || !valid(id) || is_node(id))
		return not_actor(c, id);
	get_vec(id, DOD_MOHAA_ORIGIN, from);
	from[2] -= 36.0f;	/* a grunt's origin is its body centre; nodes are at the feet */
	nodes = route_plan(id, order, from, pos, leg);
	if (!S.be.actor(id, order, leg)) {
		forget(id);
		return not_actor(c, id);
	}
	if (nodes) {
		char msg[96];
		snprintf(msg, sizeof(msg), "mohaa: %s over %d path nodes\n", name, nodes);
		S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
	}
	return 0;
}

static int c_turnto(ms_call *c)
{
	float pos[3];
	if (!dest_arg(c, 0, pos))
		return 0;	/* "turnto NULL" clears a facing target in MOHAA; holding still is the same here */
	return actor_order(c, DOD_MOHAA_TURNTO, pos);
}

/* ---- sounds: MOHAA aliases through maps/<map>.snd ---- */

static uint32_t alias_hash(const char *s)
{
	uint32_t h = 2166136261u;
	for (; *s; s++) {
		char c = (*s >= 'A' && *s <= 'Z') ? (char)(*s + 32) : *s;
		h = (h ^ (uint8_t)c) * 16777619u;
	}
	return h;
}

/* MOHAA's minimum distance (full volume inside it) to GoldSrc attenuation: 160 units is ATTN_NORM's 0.8. */
static float attn_for(float mindist)
{
	float a = mindist > 0.0f ? 128.0f / mindist : 0.8f;
	return a < 0.25f ? 0.25f : (a > 2.0f ? 2.0f : a);
}

static int channel_for(const char *name)
{
	if (!strcmp(name, "voice") || !strcmp(name, "dialog"))
		return DOD_MOHAA_CHAN_VOICE;
	if (!strcmp(name, "item"))
		return DOD_MOHAA_CHAN_ITEM;
	if (!strcmp(name, "body"))
		return DOD_MOHAA_CHAN_BODY;
	if (!strcmp(name, "weapon"))
		return DOD_MOHAA_CHAN_WEAPON;
	return DOD_MOHAA_CHAN_AUTO;
}

static void sounds_free(void)
{
	if (S.sounds)
		S.be.alloc(S.sounds, S.sounds_size, 0);
	S.sounds = NULL;
	S.sounds_size = 0;
	S.nsounds = 0;
	S.sound_text = NULL;
}

/* Parse maps/<map>.snd into one block and precache its samples. A map without one plays nothing. */
static void sounds_load(const char *mapname)
{
	char path[128];
	size_t len = 0, i, o = 0;
	char *text;
	int rows = 0;
	snprintf(path, sizeof(path), "maps/%s.snd", mapname);
	text = S.be.load_file(path, &len);
	if (!text)
		return;
	for (i = 0; i < len; i++)
		rows += text[i] == '\n';
	rows++;
	if (rows > DOD_MOHAA_MAX_SOUNDS)
		rows = DOD_MOHAA_MAX_SOUNDS;
	S.sounds_size = sizeof(DodSound) * (size_t)rows + len + 1;
	if (len + 1 > 0xFFFF || !(S.sounds = (DodSound *)S.be.alloc(NULL, 0, S.sounds_size))) {
		S.sounds_size = 0;
		S.be.print(DOD_MOHAA_PRINT_ERROR, "mohaa: sound table too big, sounds are off\n");
		if (S.be.free_file)
			S.be.free_file(text);
		return;
	}
	{
		char *strs = (char *)(S.sounds + rows);
		const char *p = text, *end = text + len;
		S.sound_text = strs;
		while (p < end && S.nsounds < rows) {
			char alias[64], sample[128], chan[16];
			float vol = 1.0f, mindist = 160.0f;
			const char *eol = memchr(p, '\n', (size_t)(end - p));
			char line[256];
			size_t n = (size_t)((eol ? eol : end) - p);
			if (n >= sizeof(line))
				n = sizeof(line) - 1;
			memcpy(line, p, n);
			line[n] = 0;
			p = eol ? eol + 1 : end;
			chan[0] = 0;
			if (line[0] == '#' || sscanf(line, "%63s %127s %f %f %15s", alias, sample, &vol, &mindist, chan) < 2)
				continue;
			{
				DodSound *r = &S.sounds[S.nsounds++];
				int k;
				r->hash = alias_hash(alias);
				r->volume = vol < 0.0f ? 0.0f : (vol > 1.0f ? 1.0f : vol);
				r->attn = attn_for(mindist);
				r->channel = (uint8_t)channel_for(chan);
				r->alias = (uint16_t)o;
				memcpy(strs + o, alias, strlen(alias) + 1);
				o += strlen(alias) + 1;
				/* the same sample under several aliases is stored and precached once */
				for (k = 0; k < S.nsounds - 1; k++)
					if (!strcmp(strs + S.sounds[k].sample, sample))
						break;
				if (k < S.nsounds - 1)
					r->sample = S.sounds[k].sample;
				else {
					r->sample = (uint16_t)o;
					memcpy(strs + o, sample, strlen(sample) + 1);
					o += strlen(sample) + 1;
					if (S.be.precache_sound)
						S.be.precache_sound(sample);
				}
			}
		}
	}
	if (S.be.free_file)
		S.be.free_file(text);
}

/* A random variant of the alias, or NULL. */
static const DodSound *sound_pick(const char *alias)
{
	uint32_t h = alias_hash(alias);
	int i, n = 0, k;
	for (i = 0; i < S.nsounds; i++)
		n += S.sounds[i].hash == h;
	if (!n) {
		for (i = 0; i < S.nmisses; i++)
			if (S.sound_misses[i] == h)
				return NULL;
		if (S.nmisses < MAX_SOUND_MISSES) {
			char msg[128];
			S.sound_misses[S.nmisses++] = h;
			snprintf(msg, sizeof(msg), "mohaa: sound '%s' is not in this map's sound table\n", alias);
			S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
		}
		return NULL;
	}
	S.rng = S.rng * 1664525u + 1013904223u;
	k = (int)((S.rng >> 16) % (uint32_t)n);
	for (i = 0; i < S.nsounds; i++)
		if (S.sounds[i].hash == h && k-- == 0)
			return &S.sounds[i];
	return NULL;
}

static void play(ms_call *c, int loop)
{
	uint32_t id = target_id(c);
	const DodSound *r = sound_pick(ms_arg_string(c, 0));
	const char *sample;
	int i, free_slot = -1;
	if (!r || !S.be.sound)
		return;
	sample = S.sound_text + r->sample;
	if (loop) {
		/* one loop per entity: a new loop replaces the old one */
		for (i = 0; i < MAX_LOOPS; i++) {
			if (S.loops[i].id == id) {
				S.be.sound(id, S.loops[i].sample, -1, 0, 0, 0);
				free_slot = i;
				break;
			}
			if (!S.loops[i].id && free_slot < 0)
				free_slot = i;
		}
		if (free_slot < 0)
			return;
		S.loops[free_slot].id = id;
		S.loops[free_slot].sample = sample;
	}
	S.be.sound(id, sample, loop, r->volume, r->attn, r->channel);
}

static int c_playsound(ms_call *c) { play(c, 0); return 0; }
static int c_loopsound(ms_call *c) { play(c, 1); return 0; }
static int c_stoploopsound(ms_call *c)
{
	uint32_t id = target_id(c);
	int i;
	for (i = 0; i < MAX_LOOPS; i++)
		if (S.loops[i].id == id) {
			if (S.be.sound)
				S.be.sound(id, S.loops[i].sample, -1, 0, 0, 0);
			S.loops[i].id = 0;
		}
	return 0;
}

/* ------------------------------------------------------------------ */
/* music: .mus moods (soundtrack, forcemusic) and stufftext cues        */
/* ------------------------------------------------------------------ */

static int mood_find(const char *name)
{
	int i;
	for (i = 0; i < S.nmoods; i++)
		if (!strcmp(S.moods[i].name, name))
			return i;
	return -1;
}

/* "sound/music/MUS_x.mp3" or "mohaa/music/x.wav" -> "sound/mohaa/music/x.wav" (tools/music.py's names) */
static void music_path(const char *src, char *out, size_t size)
{
	const char *base = src, *s;
	char name[64];
	size_t n = 0;
	for (s = src; *s; s++)
		if (*s == '/' || *s == '\\')
			base = s + 1;
	while (base[n] && base[n] != '.' && n + 1 < sizeof(name)) {
		char c = base[n];
		name[n++] = (char)(c >= 'A' && c <= 'Z' ? c - 'A' + 'a' : c);
	}
	name[n] = 0;
	snprintf(out, size, "sound/mohaa/music/%s.wav", name);
}

/* tell the game what should be playing now */
static void music_apply(void)
{
	const char *loop = "";
	if (!S.be.music)
		return;
	if (S.mood >= 0) {
		const int after = S.moods[S.mood].loop ? S.mood : S.fallback;
		if (after >= 0 && S.moods[after].loop)
			loop = S.moods[after].sample;
	}
	if (S.cue[0])
		S.be.music(S.cue, S.cue_loop ? S.cue : loop);
	else if (S.mood >= 0)
		S.be.music(S.moods[S.mood].sample, S.moods[S.mood].loop ? S.moods[S.mood].sample : loop);
	else
		S.be.music(NULL, NULL);
}

/* load music/<name>.mood; returns 1 when it had moods */
static int moods_load(const char *name)
{
	char path[128];
	size_t len = 0;
	char *text;
	const char *p, *end;
	snprintf(path, sizeof(path), "music/%s.mood", name);
	text = S.be.load_file(path, &len);
	if (!text)
		return 0;
	S.nmoods = 0;
	S.mood = S.fallback = -1;
	for (p = text, end = text + len; p < end && S.nmoods < MAX_MOODS;) {
		const char *eol = memchr(p, '\n', (size_t)(end - p));
		char line[192], mood[8], sample[74];
		float vol = 1.0f;
		int loop = 0;
		size_t n = (size_t)((eol ? eol : end) - p);
		if (n >= sizeof(line))
			n = sizeof(line) - 1;
		memcpy(line, p, n);
		line[n] = 0;
		p = eol ? eol + 1 : end;
		if (line[0] == '#' || sscanf(line, "%7s %73s %f %d", mood, sample, &vol, &loop) < 2)
			continue;
		memcpy(S.moods[S.nmoods].name, mood, sizeof(mood));
		memcpy(S.moods[S.nmoods].sample, "sound/", 6);
		memcpy(S.moods[S.nmoods].sample + 6, sample, sizeof(sample));
		S.moods[S.nmoods].loop = (uint8_t)(loop != 0);
		S.nmoods++;
	}
	if (S.be.free_file)
		S.be.free_file(text);
	return S.nmoods > 0;
}

/* "soundtrack music/m1l1.mus": that soundtrack's moods, starting on normal */
static int c_soundtrack(ms_call *c)
{
	char name[64];
	const char *src = ms_arg_string(c, 0), *base = src, *s;
	size_t n = 0;
	for (s = src; *s; s++)
		if (*s == '/' || *s == '\\')
			base = s + 1;
	while (base[n] && base[n] != '.' && n + 1 < sizeof(name)) {
		name[n] = base[n];
		n++;
	}
	name[n] = 0;
	if (!moods_load(name)) {
		/* no music staged for this map (tools/music.py output): play on without, as a missing sound does */
		char msg[128];
		snprintf(msg, sizeof(msg), "mohaa: no music/%s.mood, the level plays without music\n", name);
		S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
		return 0;
	}
	S.mood = mood_find("normal");
	S.cue[0] = 0;	/* a cue never says when it ended; a new soundtrack ends it */
	music_apply();
	return 0;
}

/* "forcemusic <mood> [fallback]" */
static int c_forcemusic(ms_call *c)
{
	const int m = mood_find(ms_arg_string(c, 0));
	if (m < 0)
		return S.nmoods ? ms_call_error(c, "no mood %s in the soundtrack", ms_arg_string(c, 0)) : 0;
	S.mood = m;
	S.fallback = ms_argc(c) > 1 ? mood_find(ms_arg_string(c, 1)) : -1;
	S.cue[0] = 0;
	music_apply();
	return 0;
}

/* "$player stufftext "tmstart sound/music/x.mp3"": MOHAA's triggered music. Other console commands are dropped:
   a script does not run commands on a GameCube player's console. */
static int c_stufftext(ms_call *c)
{
	char buf[256], *cmd, *next;
	snprintf(buf, sizeof(buf), "%s", ms_arg_string(c, 0));
	for (cmd = buf; cmd; cmd = next) {
		char word[16], arg[128];
		int n;
		next = strchr(cmd, ';');
		if (next)
			*next++ = 0;
		arg[0] = 0;
		n = sscanf(cmd, "%15s %127s", word, arg);
		if (n < 1)
			continue;
		if (!strcmp(word, "tmstop")) {
			S.cue[0] = 0;
			music_apply();
		} else if ((!strcmp(word, "tmstart") || !strcmp(word, "tmstartloop")) && n == 2) {
			music_path(arg, S.cue, sizeof(S.cue));
			S.cue_loop = word[7] == 'l';
			music_apply();
		}
	}
	return 0;
}

/* ------------------------------------------------------------------ */
/* thread commands                                                      */
/* ------------------------------------------------------------------ */

/* Accepted and dropped (see the list in register_commands). Dynamic lights cost the GameCube a lightmap rebuild per frame, so entity lights stay off;
   path links are fixed at level load (an opened door does not add a link, a closed one does not cut one). */
static int c_ignored(ms_call *c)
{
	(void)c;
	return 0;
}

/* ------------------------------------------------------------------ */
/* Cutscenes                                                            */
/* ------------------------------------------------------------------ */
/* MOHAA plays its in-game cutscenes in the running level, not as films. m1l1's opening is the model case: an
 * animated path model (vehicles/gmctruckpath_opening.tik) carries tags for the truck, each squad member and the
 * camera; a script loop copies those tags onto the truck, the actors and a script_origin every frame; the player is
 * put on a turret glued to that origin with physics off, and handed control back when the ride ends. Actors play
 * scripted animations and the script waits on "animdone". So the pieces here are:
 *   - model / anim / anim_scripted / anim_noclip: which baked model and animation an entity plays (maps/<map>.tags,
 *     mohaa-gc tools/mohaa_tags.py), and "animdone" when that animation's real length has passed;
 *   - gettagposition / gettagangles: the tag at the animation's current time, placed by the entity's origin and
 *     angles, so everything the script hangs on the path moves along it;
 *   - glue / unglue: an entity (or the player) follows another every frame;
 *   - physics_off / physics_on, freezeplayer / releaseplayer: the player's own movement stops and starts;
 *   - doUse $player on a turret and its "viewangles": the player's eyes ride the turret and their view turns as
 *     the script turns it, while they can still look around (GameCube pad: the stick still looks);
 *   - drawhud: MOHAA's HUD switch; a locked player also loses the crosshair and weapon readout;
 *   - aimat + animscript ".../shoot.scr", radiusdamage: a scripted shot or blast that sets off MOHAA damage
 *     triggers (m1l1's bazooka hits the papers truck to end the ride).
 * Without a .tags file the commands still run: tags sit at the entity's origin and animations last a second. */

static DodCine *cine(uint32_t id, int create)
{
	int i, free_slot = -1;
	if (!id)
		return NULL;
	for (i = 0; i < DOD_MOHAA_MAX_CINE; i++) {
		if (S.cine[i].id == id)
			return &S.cine[i];
		if (!S.cine[i].id && free_slot < 0)
			free_slot = i;
	}
	if (!create || free_slot < 0)
		return NULL;
	memset(&S.cine[free_slot], 0, sizeof(DodCine));
	S.cine[free_slot].id = id;
	S.cine[free_slot].model = -1;
	return &S.cine[free_slot];
}

static uint32_t the_player(void)
{
	uint32_t id = 0;
	if (S.be.find("player", &id, 1) < 1 || !valid(id))
		return 0;
	return id;
}

static int is_player(uint32_t id)
{
	return id && id == the_player();
}

static const char *anim_name(ms_call *c, int i, char *buf, size_t size)
{
	return ms_tostring(ms_arg(c, i), buf, size);
}

/* "$e model <tik>" */
static int c_model(ms_call *c)
{
	char buf[128];
	DodCine *k = cine(target_id(c), 1);
	if (k) {
		k->model = MohaaTags_Model(&S.tags, MohaaTags_Hash(anim_name(c, 0, buf, sizeof(buf))));
		k->anim = 0;
	}
	return 0;
}

/* "$e anim <name>" (and anim_scripted, anim_noclip): animdone when it would have ended */
static int c_anim(ms_call *c)
{
	char buf[96];
	DodCine *k = cine(target_id(c), 1);
	float len;
	if (!k)
		return 0;
	k->anim = MohaaTags_Hash(anim_name(c, 0, buf, sizeof(buf)));
	len = MohaaTags_Length(&S.tags, k->model, k->anim);
	k->anim_start = S.now;
	k->anim_end = S.now + (len >= 0.0f ? len : DOD_MOHAA_ANIM_DEFAULT);
	k->done_pending = 1;
	return 0;
}

static void apply_hud(void)
{
	const int bits = (S.drawhud_off ? DOD_MOHAA_HUD_ALL : 0) | (S.player_locked || S.ride ? DOD_MOHAA_HUD_WEAPON : 0);
	if (bits == S.hud_sent || !S.be.hud)
		return;
	S.hud_sent = bits;
	S.be.hud(bits);
}

static void lock_player(uint32_t id, int on)
{
	if (!id)
		return;
	if (on)
		S.player = id;
	S.player_locked = on;
	if (S.be.player_lock)
		S.be.player_lock(id, on);
	apply_hud();
}

/* "$e physics_off" / "physics_on": the player stops and starts moving; other entities have no physics to stop */
static int c_physics(ms_call *c)
{
	const uint32_t id = target_id(c);
	if (is_player(id))
		lock_player(id, strstr(ms_call_name(c), "off") != NULL);
	return 0;
}

/* "freezeplayer" / "releaseplayer" */
static int c_freezeplayer(ms_call *c)
{
	lock_player(the_player(), ms_call_name(c)[0] == 'f');
	return 0;
}

/* "$e glue $parent [angles]": follow parent's origin (and angles unless 0) until unglued */
static int c_glue(ms_call *c)
{
	const uint32_t id = target_id(c);
	const ms_value *p = ms_arg(c, 0);
	DodCine *k;
	if (p->type != MS_ENTITY || !valid(p->u.id) || p->u.id == id || !(k = cine(id, 1)))
		return 0;
	k->glue = p->u.id;
	k->glue_angles = ms_argc(c) > 1 ? ms_arg_int(c, 1) != 0 : 1;
	if (is_player(id))
		S.player = id;
	return 0;
}

static int c_unglue(ms_call *c)
{
	DodCine *k = cine(target_id(c), 0);
	if (k)
		k->glue = 0;
	return 0;
}

/* "$turret doUse $player": the player gets on (or, again, off) the turret. The VM folds case, so this is also
   "douse" (put out a fire), which names no player and stays a no-op. */
static int c_douse(ms_call *c)
{
	const uint32_t id = target_id(c);
	const ms_value *p = ms_arg(c, 0);
	if (p->type != MS_ENTITY || !is_player(p->u.id))
		return 0;
	if (S.ride == id) {
		S.ride = 0;
	} else {
		S.ride = id;
		S.ride_fresh = 1;
		S.player = p->u.id;
	}
	apply_hud();
	return 0;
}

/* "drawhud 0|1" */
static int c_drawhud(ms_call *c)
{
	S.drawhud_off = ms_arg_int(c, 0) == 0;
	apply_hud();
	return 0;
}

/* "$actor aimat <target>" */
static int c_aimat(ms_call *c)
{
	const ms_value *t = ms_arg(c, 0);
	DodCine *k = cine(target_id(c), 1);
	if (!k)
		return 0;
	k->has_aim = 0;
	k->aim_id = 0;
	if (t->type == MS_ENTITY && valid(t->u.id)) {
		k->has_aim = 1;
		k->aim_id = t->u.id;
	} else if (t->type == MS_VECTOR) {
		k->has_aim = 1;
		scale_in(t->u.v, k->aim);
	}
	return 0;
}

#define DOD_MOHAA_SHOT_RADIUS 48.0f	/* GoldSrc units round a scripted shot's aim point that it hurts */
#define DOD_MOHAA_SHOT_DAMAGE 200.0f	/* a rocket's worth: scripted shots are bazookas and set pieces */

/* "$actor animscript anim/shoot.scr": actors have no weapons to fire here, so a scripted shot lands at the aim point */
static int c_animscript(ms_call *c)
{
	char buf[96];
	const uint32_t id = target_id(c);
	DodCine *k = cine(id, 0);
	float at[3];
	if (!k || !k->has_aim || !strstr(anim_name(c, 0, buf, sizeof(buf)), "shoot") || !S.be.damage_at)
		return 0;
	if (k->aim_id) {
		if (!valid(k->aim_id))
			return 0;
		get_vec(k->aim_id, DOD_MOHAA_ORIGIN, at);
	} else {
		memcpy(at, k->aim, sizeof(at));
	}
	S.be.damage_at(id, at, DOD_MOHAA_SHOT_RADIUS, DOD_MOHAA_SHOT_DAMAGE);
	return 0;
}

/* "radiusdamage <origin> <damage> <radius> [constant]" */
static int c_radiusdamage(ms_call *c)
{
	float o[3], g[3];
	if (!S.be.damage_at || ms_arg(c, 0)->type != MS_VECTOR)
		return 0;
	ms_arg_vector(c, 0, o);
	scale_in(o, g);
	S.be.damage_at(0, g, ms_arg_float(c, 2) * DOD_MOHAA_SCALE, ms_arg_float(c, 1));
	return 0;
}

/* A tag of the entity's model now, in MOHAA world units and angles. 0 when it has no such baked tag. */
static int tag_now(uint32_t id, const char *tag, float pos[3], float ang[3])
{
	const DodCine *k = cine(id, 0);
	const MohaaTagModel *m;
	float o[3], a[3], p[3], q[4], tm[3][3], em[3][3], wm[3][3];
	int t, an, r, cc;
	if (!k || k->model < 0 || k->model >= S.tags.nmodels)
		return 0;
	m = &S.tags.models[k->model];
	t = MohaaTags_Tag(m, MohaaTags_Hash(tag));
	if (t < 0 || !m->nanims)
		return 0;
	an = k->anim ? MohaaTags_Anim(m, k->anim) : -1;
	if (an < 0)
		an = MohaaTags_Anim(m, MohaaTags_Hash("idle"));
	if (an < 0)
		an = 0;
	MohaaTags_Sample(m, an, t, k->anim && MohaaTags_Anim(m, k->anim) == an ? S.now - k->anim_start : 0.0f, p, q);
	get_vec(id, DOD_MOHAA_ORIGIN, o);
	scale_out(o, o);
	get_vec(id, DOD_MOHAA_ANGLES, a);
	MohaaTags_AnglesMatrix(a, em);
	MohaaTags_QuatMatrix(q, tm);
	for (r = 0; r < 3; r++) {
		pos[r] = o[r] + em[r][0] * p[0] + em[r][1] * p[1] + em[r][2] * p[2];
		for (cc = 0; cc < 3; cc++)
			wm[r][cc] = em[r][0] * tm[0][cc] + em[r][1] * tm[1][cc] + em[r][2] * tm[2][cc];
	}
	MohaaTags_MatrixAngles(wm, ang);
	return 1;
}

/* "$e gettagposition <tag>" / "gettagangles": the baked tag when there is one; otherwise the tag sits at the
   entity's own origin and faces its way (good enough for spawning effects or aiming at a bone) */
static int c_gettag(ms_call *c)
{
	char buf[96];
	float v[3], out[3], ang[3];
	const uint32_t id = target_id(c);
	const int angles = strstr(ms_call_name(c), "angles") != NULL;
	if (!valid(id)) {
		ms_return(c, NULL);
		return 0;
	}
	if (!is_node(id) && tag_now(id, anim_name(c, 0, buf, sizeof(buf)), out, ang)) {
		ms_return_vector(c, angles ? ang : out);
		return 0;
	}
	get_vec(id, angles ? DOD_MOHAA_ANGLES : DOD_MOHAA_ORIGIN, v);
	if (angles)
		memcpy(out, v, sizeof(v));
	else
		scale_out(v, out);
	ms_return_vector(c, out);
	return 0;
}

/* Once a frame, after the scripts ran: animations that ended, glued entities, the held player and their view. */
static void cine_think(void)
{
	int i;
	uint32_t player = S.player;
	for (i = 0; i < DOD_MOHAA_MAX_CINE && S.vm; i++) {
		DodCine *k = &S.cine[i];
		if (!k->id)
			continue;
		if (!valid(k->id)) {
			memset(k, 0, sizeof(*k));
			continue;
		}
		if (k->done_pending && S.now >= k->anim_end) {
			ms_value ent = ms_entity(k->id);
			k->done_pending = 0;
			ms_notify(S.vm, &ent, "animdone");
		}
	}
	for (i = 0; i < DOD_MOHAA_MAX_CINE; i++) {
		DodCine *k = &S.cine[i];
		float v[3];
		if (!k->id || !k->glue || k->id == player)
			continue;
		if (!valid(k->glue)) {
			k->glue = 0;
			continue;
		}
		get_vec(k->glue, DOD_MOHAA_ORIGIN, v);
		S.be.set_vec(k->id, DOD_MOHAA_ORIGIN, v);
		if (k->glue_angles) {
			get_vec(k->glue, DOD_MOHAA_ANGLES, v);
			S.be.set_vec(k->id, DOD_MOHAA_ANGLES, v);
		}
	}
	if (!player || !valid(player)) {
		S.player = 0;
		return;
	}
	if (S.ride && !valid(S.ride))
		S.ride = 0;
	{
		const DodCine *pk = cine(player, 0);
		float v[3];
		if (S.ride) {
			/* the turret's view position is its origin: the player's eyes go there */
			get_vec(S.ride, DOD_MOHAA_ORIGIN, v);
			if (S.be.place_player)
				S.be.place_player(player, v, 1);
		} else if (pk && pk->glue && valid(pk->glue)) {
			get_vec(pk->glue, DOD_MOHAA_ORIGIN, v);
			if (S.be.place_player)
				S.be.place_player(player, v, 0);
		}
	}
	if (S.ride && S.be.view) {
		const DodCine *rk = cine(S.ride, 0);
		if (rk && rk->has_view) {
			if (S.ride_fresh) {
				const float a[3] = {rk->view[0], rk->view[1], 0.0f};
				S.be.view(player, a, 0);
				S.ride_fresh = 0;
			} else if (rk->view[1] != S.ride_yaw) {
				const float d[3] = {0.0f, rk->view[1] - S.ride_yaw, 0.0f};
				S.be.view(player, d, 1);
			}
			S.ride_yaw = rk->view[1];
		}
	}
	if (!S.ride && !S.player_locked && !(cine(player, 0) && cine(player, 0)->glue))
		S.player = 0;
}

/* "$e velocity (x y z)": a push in MOHAA units per second */
/* "$e damage $attacker 50 ...": the amount comes off its health */
static int c_damage(ms_call *c)
{
	const uint32_t id = target_id(c);
	const float amount = ms_arg_float(c, 1);
	if (valid(id) && !is_node(id) && amount > 0.0f)
		S.be.set_health(id, S.be.get_health(id) - amount);
	return 0;
}

static int c_velocity(ms_call *c)
{
	float v[3], g[3];
	static const float zero[3] = {0, 0, 0};
	ms_arg_vector(c, 0, v);
	scale_in(v, g);
	S.be.set_velocity(target_id(c), g, zero);
	return 0;
}

/* "setcvar <name> <value>" */
static int c_setcvar(ms_call *c)
{
	if (S.be.set_cvar && ms_argc(c) >= 2)
		S.be.set_cvar(ms_arg_string(c, 0), ms_arg_string(c, 1));
	return 0;
}

/* "addobjective <index> <state> <text> [location]" keeps the text; "setcurrentobjective <index>" shows it */
static int c_addobjective(ms_call *c)
{
	const int i = ms_arg_int(c, 0);
	if (i >= 1 && i <= 8 && ms_argc(c) >= 3)
		snprintf(S.objectives[i - 1], sizeof(S.objectives[0]), "%s", ms_arg_string(c, 2));
	return 0;
}

static int c_setcurrentobjective(ms_call *c)
{
	const int i = ms_arg_int(c, 0);
	if (i >= 1 && i <= 8 && S.objectives[i - 1][0]) {
		char msg[128];
		snprintf(msg, sizeof(msg), "Objective: %s", S.objectives[i - 1]);
		S.be.print(DOD_MOHAA_PRINT_CENTER, msg);
	}
	return 0;
}

/* "isalive $guy": 1 while the entity exists and has health left */
static int c_isalive(ms_call *c)
{
	const ms_value *v = ms_arg(c, 0);
	int alive = v->type == MS_ENTITY && valid(v->u.id) && !is_node(v->u.id) && S.be.get_health(v->u.id) > 0.0f;
	ms_return_int(c, alive);
	return 0;
}

/* "getcvar <name>": the cvar's string ("" when unknown) */
static int c_getcvar(ms_call *c)
{
	const char *v = S.be.get_cvar ? S.be.get_cvar(ms_arg_string(c, 0)) : NULL;
	ms_return_string(c, v ? v : "");
	return 0;
}

/* "fadeout <time> <r> <g> <b> <alpha> [mode]" / "fadein ...": a screen fade for every player */
static int c_fade(ms_call *c)
{
	const int out = ms_call_name(c)[4] == 'o' || ms_call_name(c)[4] == 'O';
	const float t = ms_argc(c) > 0 ? ms_arg_float(c, 0) : 1.0f;
	const float r = ms_argc(c) > 1 ? ms_arg_float(c, 1) : 0.0f, g = ms_argc(c) > 2 ? ms_arg_float(c, 2) : 0.0f;
	const float b = ms_argc(c) > 3 ? ms_arg_float(c, 3) : 0.0f, a = ms_argc(c) > 4 ? ms_arg_float(c, 4) : 1.0f;
	if (S.be.fade)
		S.be.fade(t < 0.0f ? 0.0f : t, r, g, b, a < 0.0f ? 0.0f : (a > 1.0f ? 1.0f : a), out);
	return 0;
}

static void trigger_value(const ms_value *v)
{
	if (v->type == MS_ENTITY) {
		const char *tn = valid(v->u.id) ? S.be.get_str(v->u.id, DOD_MOHAA_TARGETNAME) : NULL;
		if (tn && *tn)
			S.be.use_targets(tn);
	} else if (v->type == MS_CARRAY || v->type == MS_ARRAY) {
		/* every entity in "$guys" shares the targetname, so one use fires them all */
		const ms_value *first = ms_array_item(v, 0);
		if (first)
			trigger_value(first);
	} else if (ms_string_text(v)) {
		const char *s = ms_string_text(v);
		S.be.use_targets(s[0] == '$' ? s + 1 : s);
	}
}

static int c_trigger(ms_call *c)
{
	trigger_value(ms_arg(c, 0));
	return 0;
}

/* "3" -> 3, "0.5" -> 0.5, anything else stays a string (the VM's own value for a numeric key) */
static ms_value key_value(const char *value)
{
	char *end;
	long i = strtol(value, &end, 10);
	double f;
	if (*value && !*end)
		return ms_int((int32_t)i);
	f = strtod(value, &end);
	if (*value && !*end)
		return ms_float((float)f);
	return ms_string(S.vm, value);
}

void Dod_MohaaEntityKey(uint32_t id, const char *key, const char *value)
{
	ms_value v;
	if (!S.vm || !id || !key || !value)
		return;
	v = key_value(value);
	/* MOHAA's '#' marks a key as a script variable; the variable's name has none (#set -> $ent.set) */
	ms_set_entity_var(S.vm, id, key[0] == '#' ? key + 1 : key, &v);
	ms_release(S.vm, v);
}

void Dod_MohaaEntityMoved(uint32_t from, uint32_t to)
{
	if (S.vm && from && to)
		ms_move_entity_vars(S.vm, from, to);
}

void Dod_MohaaSetOther(uint32_t id)
{
	ms_value v = ms_nil();
	if (!S.vm)
		return;
	if (id && valid(id))
		v = ms_entity(id);
	else
		v.type = MS_NULL;
	ms_set_parm(S.vm, "other", &v);
}

static int c_spawn(ms_call *c)
{
	const char *keys[16], *vals[16];
	char origin[64];
	int n = 0, i;
	uint32_t id;
	for (i = 1; i + 1 < ms_argc(c) && n < 16; i += 2) {
		keys[n] = ms_arg_string(c, i);
		if (!strcmp(keys[n], "origin")) {
			float v[3];
			ms_arg_vector(c, i + 1, v);
			scale_in(v, v);
			snprintf(origin, sizeof(origin), "%g %g %g", v[0], v[1], v[2]);
			vals[n] = origin;
		} else
			vals[n] = ms_arg_string(c, i + 1);
		n++;
	}
	id = S.be.spawn(ms_arg_string(c, 0), keys, vals, n);
	if (!id)
		return ms_call_error(c, "could not spawn '%s'", ms_arg_string(c, 0));
	for (i = 0; i < n; i++)
		if (keys[i][0] == '#')
			Dod_MohaaEntityKey(id, keys[i], vals[i]);
	ms_return_entity(c, id);
	return 0;
}

/* A vehicle's turret: there are no separate turret entities yet, so the vehicle answers for its turrets and the
   turret commands (setaimtarget, ...) are no-ops on it, instead of every one failing on NIL. */
static int c_queryturretslotentity(ms_call *c)
{
	ms_return(c, ms_call_target(c));
	return 0;
}

static int c_centerprint(ms_call *c)
{
	S.be.print(DOD_MOHAA_PRINT_CENTER, ms_arg_string(c, 0));
	return 0;
}

static void register_commands(ms_vm *vm)
{
	static const struct { const char *name; unsigned on; ms_cmd_fn fn; } table[] = {
		{"hide", MS_ON_ENTITY, c_hide},
		{"show", MS_ON_ENTITY, c_show},
		{"notsolid", MS_ON_ENTITY, c_notsolid},
		{"solid", MS_ON_ENTITY, c_solid},
		{"remove", MS_ON_ENTITY, c_remove},
		{"delete", MS_ON_ENTITY, c_remove},
		{"origin", MS_ON_ENTITY, c_origin},
		{"angles", MS_ON_ENTITY, c_angles},
		{"health", MS_ON_ENTITY, c_health},
		{"time", MS_ON_ENTITY, c_time},
		{"moveto", MS_ON_ENTITY, c_moveto},
		{"moveup", MS_ON_ENTITY, c_move_dir},
		{"movedown", MS_ON_ENTITY, c_move_dir},
		{"movenorth", MS_ON_ENTITY, c_move_dir},
		{"movesouth", MS_ON_ENTITY, c_move_dir},
		{"moveeast", MS_ON_ENTITY, c_move_dir},
		{"movewest", MS_ON_ENTITY, c_move_dir},
		{"rotateto", MS_ON_ENTITY, c_rotateto},
		{"rotatex", MS_ON_ENTITY, c_rotate_axis},
		{"rotatey", MS_ON_ENTITY, c_rotate_axis},
		{"rotatez", MS_ON_ENTITY, c_rotate_axis},
		{"move", MS_ON_ENTITY, c_move},
		{"waitmove", MS_ON_ENTITY, c_waitmove},
		{"playsound", MS_ON_ENTITY, c_playsound},
		{"loopsound", MS_ON_ENTITY, c_loopsound},
		{"stoploopsound", MS_ON_ENTITY, c_stoploopsound},
		{"ai_on", MS_ON_ENTITY, c_ai_on},
		{"ai_off", MS_ON_ENTITY, c_ai_off},
		{"attackplayer", MS_ON_ENTITY, c_attackplayer},
		{"runto", MS_ON_ENTITY, c_goto},
		{"walkto", MS_ON_ENTITY, c_goto},
		{"turnto", MS_ON_ENTITY, c_turnto},
		{"lookat", MS_ON_ENTITY, c_turnto},
		{"stufftext", MS_ON_ENTITY, c_stufftext},
		{"soundtrack", MS_ON_THREAD | MS_ON_ENTITY, c_soundtrack},
		{"forcemusic", MS_ON_THREAD | MS_ON_ENTITY, c_forcemusic},
		{"isalive", MS_ON_THREAD, c_isalive},
		{"gettagposition", MS_ON_ENTITY, c_gettag},
		{"gettagangles", MS_ON_ENTITY, c_gettag},
		{"velocity", MS_ON_ENTITY, c_velocity},
		{"physics_velocity", MS_ON_ENTITY, c_velocity},
		{"damage", MS_ON_ENTITY, c_damage},
		{"say", MS_ON_ENTITY, c_playsound},	/* an actor's line: its sound alias, from the actor */
		{"rotatexup", MS_ON_ENTITY, c_rotate_rel},
		{"rotatexdown", MS_ON_ENTITY, c_rotate_rel},
		{"rotateyup", MS_ON_ENTITY, c_rotate_rel},
		{"rotateydown", MS_ON_ENTITY, c_rotate_rel},
		{"rotatezup", MS_ON_ENTITY, c_rotate_rel},
		{"rotatezdown", MS_ON_ENTITY, c_rotate_rel},
		{"followpath", MS_ON_ENTITY, c_followpath},
		/* cutscenes (see "Cutscenes" above) */
		{"model", MS_ON_ENTITY, c_model},
		{"anim", MS_ON_ENTITY, c_anim},
		{"anim_scripted", MS_ON_ENTITY, c_anim},
		{"anim_noclip", MS_ON_ENTITY, c_anim},
		{"animscript", MS_ON_ENTITY, c_animscript},
		{"aimat", MS_ON_ENTITY, c_aimat},
		{"glue", MS_ON_ENTITY, c_glue},
		{"unglue", MS_ON_ENTITY, c_unglue},
		{"physics_off", MS_ON_ENTITY, c_physics},
		{"physics_on", MS_ON_ENTITY, c_physics},
		{"douse", MS_ON_ENTITY, c_douse},
		{"freezeplayer", MS_ON_THREAD, c_freezeplayer},
		{"releaseplayer", MS_ON_THREAD, c_freezeplayer},
		{"drawhud", MS_ON_THREAD, c_drawhud},
		{"radiusdamage", MS_ON_THREAD, c_radiusdamage},
		{"endpath", MS_ON_ENTITY, c_stopdrive},
		{"forceactivate", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"setcvar", MS_ON_THREAD, c_setcvar},
		{"addobjective", MS_ON_THREAD, c_addobjective},
		{"setcurrentobjective", MS_ON_THREAD, c_setcurrentobjective},
		{"lighton", MS_ON_ENTITY, c_ignored},
		{"light", MS_ON_ENTITY, c_ignored},
		/* animation, TIKI models, attachment, vehicles and turrets, weapons and inventory: none of it exists on the
		   GameCube side yet. Accepted so a mission keeps going; README "Not yet" lists what they would need. */
		{"american", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"attach", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"bind", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"forcelegsstate", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"gren_awareness", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"holster", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"nodamage", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"takedamage", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"scale", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"setplayerusable", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"threatbias", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"unbind", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"turnspeed", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"vehiclespeed", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"burstfiresettings", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"removeondeath", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"rendereffects", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"tracerfrequency", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"triggereffect", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"setaimtarget", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"accuracy", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"bulletdamage", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"firedelay", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"maxyawoffset", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"pitchcaps", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"ammo", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"heal", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"item", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"takeall", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"useweaponclass", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"dontdropweapons", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"unholster", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		{"detach", MS_ON_ENTITY | MS_ON_THREAD, c_ignored},
		/* scripted HUD elements (m6l1a's mg42 overlay): there is no matching HUD element on the GoldSrc side yet */
		{"huddraw_shader", MS_ON_THREAD, c_ignored},
		{"huddraw_align", MS_ON_THREAD, c_ignored},
		{"huddraw_rect", MS_ON_THREAD, c_ignored},
		{"huddraw_virtualsize", MS_ON_THREAD, c_ignored},
		{"huddraw_color", MS_ON_THREAD, c_ignored},
		{"huddraw_alpha", MS_ON_THREAD, c_ignored},
		{"huddraw_string", MS_ON_THREAD, c_ignored},
		{"huddraw_font", MS_ON_THREAD, c_ignored},
		{"lightoff", MS_ON_ENTITY, c_ignored},
		{"lightradius", MS_ON_ENTITY, c_ignored},
		{"lightcolor", MS_ON_ENTITY, c_ignored},
		{"disconnect_paths", MS_ON_ENTITY, c_ignored},
		{"connect_paths", MS_ON_ENTITY, c_ignored},
		{"getcvar", MS_ON_THREAD, c_getcvar},
		{"fadeout", MS_ON_THREAD, c_fade},
		{"fadein", MS_ON_THREAD, c_fade},
		{"trigger", MS_ON_THREAD, c_trigger},
		{"spawn", MS_ON_THREAD, c_spawn},
		{"centerprint", MS_ON_THREAD, c_centerprint},
		{"queryturretslotentity", MS_ON_ENTITY, c_queryturretslotentity},
		{"drive", MS_ON_ENTITY, c_drive},
		{"modifydrive", MS_ON_ENTITY, c_modifydrive},
		{"stop", MS_ON_ENTITY, c_stopdrive},
		{"fullstop", MS_ON_ENTITY, c_stopdrive},
		/* vehicle seats and locks: no one rides a vehicle yet */
		{"lock", MS_ON_ENTITY, c_ignored},
		{"unlock", MS_ON_ENTITY, c_ignored},
		{"attachdriverslot", MS_ON_ENTITY, c_ignored},
		{"attachpassengerslot", MS_ON_ENTITY, c_ignored},
		{"attachturretslot", MS_ON_ENTITY, c_ignored},
		{"detachdriverslot", MS_ON_ENTITY, c_ignored},
		{"detachpassengerslot", MS_ON_ENTITY, c_ignored},
		{"detachturretslot", MS_ON_ENTITY, c_ignored},
		{NULL, 0, NULL}
	};
	int i;
	for (i = 0; table[i].name; i++)
		ms_register(vm, table[i].name, table[i].on, table[i].fn, NULL);
}

/* ------------------------------------------------------------------ */
/* lifecycle                                                            */
/* ------------------------------------------------------------------ */

void Dod_MohaaShutdown(void)
{
	if (S.vm)
		ms_destroy(S.vm);
	S.vm = NULL;
	memset(S.movers, 0, sizeof(S.movers));
	S.nunknown = 0;
	S.ticks = 0;
	sounds_free();
	memset(S.loops, 0, sizeof(S.loops));
	S.nmisses = 0;
	S.nmoods = 0;
	S.mood = S.fallback = -1;
	S.cue[0] = 0;
	memset(S.objectives, 0, sizeof(S.objectives));
	MohaaPaths_Free(&S.paths);
	S.path_links = 0;
	memset(S.routes, 0, sizeof(S.routes));
	MohaaTags_Free(&S.tags, S.be.alloc);
	memset(S.cine, 0, sizeof(S.cine));
	if (S.player_locked && S.be.player_lock && S.player)
		S.be.player_lock(S.player, 0);	/* a level that ends mid-cutscene must not leave the player stuck */
	S.player = S.ride = 0;
	S.player_locked = S.ride_fresh = S.drawhud_off = 0;
	if (S.hud_sent > 0 && S.be.hud)
		S.be.hud(0);
	S.hud_sent = -1;
	memset(&g_pool, 0, sizeof(g_pool));
	heap_drop();   /* normally empty: the VM freed its blocks */
}

void Dod_MohaaDropPool(void)
{
	if (S.be.alloc != pool_alloc)
		return;
	/* the region is gone (or about to be reused): forget everything in it without freeing */
	S.vm = NULL;
	S.sounds = NULL;
	memset(&S.tags, 0, sizeof(S.tags));
	Dod_MohaaShutdown();   /* frees the overflow blocks on the heap too */
	S.be.alloc = default_alloc;
}

int Dod_MohaaPathNodes(int *links)
{
	if (links)
		*links = S.path_links;
	return S.paths.count;
}

static int walk_test(void *ctx, const float a[3], const float b[3])
{
	(void)ctx;
	return S.be.walkable(a, b);
}

/* maps/<map>.nodes: loaded for names, linked when the game can test walks */
static void node_key(void *ctx, int node, const char *key, const char *value)
{
	(void)ctx;
	Dod_MohaaEntityKey(DOD_MOHAA_NODE_ID | (uint32_t)node, key, value);
}

/* maps/<map>.tags (mohaa-gc tools/mohaa_tags.py): cutscene model tags and animation lengths */
static void tags_load(const char *mapname)
{
	char path[128], msg[320];
	size_t len = 0;
	char *data;
	int arena_data = 0;
	snprintf(path, sizeof(path), "maps/%s.tags", mapname);
	data = S.be.load_file(path, &len);
	if (!data)
		return;
	/* A large MTAG cannot fit in the fragmented engine heap on maps like m1l1. The baker
	 * writes MTGC plus small numbered pieces; assemble them in the reserved script arena. */
	if (len >= 20 && !memcmp(data, "MTGC", 4)) {
		const unsigned char *h = (const unsigned char *)data;
		uint32_t version = (uint32_t)h[4] | ((uint32_t)h[5] << 8) | ((uint32_t)h[6] << 16) | ((uint32_t)h[7] << 24);
		uint32_t total = (uint32_t)h[8] | ((uint32_t)h[9] << 8) | ((uint32_t)h[10] << 16) | ((uint32_t)h[11] << 24);
		uint32_t chunk = (uint32_t)h[12] | ((uint32_t)h[13] << 8) | ((uint32_t)h[14] << 16) | ((uint32_t)h[15] << 24);
		uint32_t count = (uint32_t)h[16] | ((uint32_t)h[17] << 8) | ((uint32_t)h[18] << 16) | ((uint32_t)h[19] << 24);
		char *manifest = data, *assembled = NULL;
		int ok = version == 1 && total > 0 && total <= 4u * 1024u * 1024u && chunk >= 512 && chunk <= 16384 &&
			count == (total + chunk - 1) / chunk;
		if (ok)
			assembled = (char *)S.be.alloc(NULL, 0, total);
		if (!assembled)
			ok = 0;
		if (ok) {
			for (uint32_t i = 0, offset = 0; i < count; i++) {
				char part_path[160];
				size_t part_len = 0;
				char *part;
				snprintf(part_path, sizeof(part_path), "maps/%s.tags.%03u", mapname, (unsigned)i);
				part = S.be.load_file(part_path, &part_len);
				if (!part || part_len != (size_t)((total - offset) < chunk ? total - offset : chunk)) {
					ok = 0;
					if (part && S.be.free_file) S.be.free_file(part);
					break;
				}
				memcpy(assembled + offset, part, part_len);
				offset += (uint32_t)part_len;
				if (S.be.free_file) S.be.free_file(part);
			}
		}
		if (S.be.free_file) S.be.free_file(manifest);
		if (!ok) {
			if (assembled) S.be.alloc(assembled, total, 0);
			S.be.print(DOD_MOHAA_PRINT_CONSOLE, "mohaa: tag chunks are incomplete or out of memory\n");
			return;
		}
		data = assembled;
		len = total;
		arena_data = 1;
	}
	if (MohaaTags_Load(&S.tags, data, len, S.be.alloc))
		snprintf(msg, sizeof(msg), "mohaa: %s: %d models with tags, %d animation lengths, %u KB\n", path,
			S.tags.nmodels, S.tags.ndur, (unsigned)(S.tags.size / 1024u));
	else
		snprintf(msg, sizeof(msg), "mohaa: %s is unreadable or did not fit, cutscene tags sit at entity origins\n", path);
	S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
	if (arena_data)
		S.be.alloc(data, len, 0);
	else if (S.be.free_file)
		S.be.free_file(data);
}

static void nodes_load(const char *mapname)
{
	char path[128], msg[256];
	size_t len = 0;
	char *text;
	int i, k, traces = 0;
	snprintf(path, sizeof(path), "maps/%s.nodes", mapname);
	text = S.be.load_file(path, &len);
	if (!text)
		return;
	MohaaPaths_Load(&S.paths, text, len);
	MohaaPaths_Keys(text, len, S.paths.count, node_key, NULL);
	if (S.be.free_file)
		S.be.free_file(text);
	if (S.be.walkable && S.paths.count > 1)
		traces = MohaaPaths_Link(&S.paths, walk_test, NULL, MOHAA_PATH_REACH);
	for (i = 0; i < S.paths.count; i++)
		for (k = 0; k < MOHAA_PATH_LINKS && S.paths.link[i][k] != MOHAA_PATH_NONE; k++)
			S.path_links++;
	S.path_links /= 2;
	snprintf(msg, sizeof(msg), "mohaa: %d path nodes from %s, %d links (%d walk tests)\n", S.paths.count, path,
		S.path_links, traces);
	S.be.print(DOD_MOHAA_PRINT_CONSOLE, msg);
}

int Dod_MohaaLevelInit(const DodMohaaBackend *backend, const char *mapname, float now, size_t memory_budget)
{
	char path[128];
	size_t len = 0;
	char *text;
	ms_host host;
	ms_config cfg;

	Dod_MohaaShutdown();
	if (!backend || !mapname || !*mapname)
		return 0;
	S.be = *backend;
	if (!S.be.alloc) {
		if (S.be.pool && MohaaPool_Init(&g_pool, S.be.pool, S.be.pool_size)) {
			int r;
			for (r = 0; r < 7; r++)
				if (S.be.pool_more[r] && S.be.pool_more_size[r])
					MohaaPool_AddRegion(&g_pool, S.be.pool_more[r], S.be.pool_more_size[r]);
			/* the budget stays as asked: what the pool cannot hold goes to the heap (m5l2b got one 64 KB piece) */
			S.be.alloc = pool_alloc;
		} else {
			S.be.alloc = default_alloc;
		}
	}
	S.now = now;
	snprintf(path, sizeof(path), "maps/%s.scr", mapname);
	snprintf(S.level_script, sizeof(S.level_script), "%s", path);
	text = S.be.load_file(path, &len);
	if (!text)
		return 0;   /* not a MOHAA map: no VM, no cost */

	memset(&host, 0, sizeof(host));
	host.alloc = h_alloc;
	host.load_file = h_load;
	host.free_file = h_free;
	host.print = h_print;
	host.find_targetname = h_find;
	host.entity_valid = h_valid;
	host.get_field = h_get_field;
	host.set_field = h_set_field;
	host.unknown_command = h_unknown;
	if (S.be.alloc == pool_alloc)
		host.scratch = h_scratch;
	memset(&cfg, 0, sizeof(cfg));
	cfg.memory_budget = memory_budget;
	S.budget = memory_budget;
	S.vm = ms_create(&host, &cfg);
	if (!S.vm) {
		if (S.be.free_file)
			S.be.free_file(text);
		S.be.print(DOD_MOHAA_PRINT_ERROR, "mohaa: cannot create the script VM\n");
		return 0;
	}
	register_commands(S.vm);
	S.rng = 0x2545F491u ^ (uint32_t)(now * 1000.0f);   /* variants differ from run to run */
	sounds_load(mapname);
	nodes_load(mapname);
	tags_load(mapname);
	/* a level that never names its soundtrack plays music/<map>.mood (MOHAA's .mus files are named after the map) */
	if (moods_load(mapname)) {
		S.mood = mood_find("normal");
		music_apply();
	}
	/* compile now, so a level whose script cannot load says so at once; run it on the first frame, once the
	   map's entities have spawned (this runs while the world entity spawns, before any other) */
	{
		const int ok = ms_load_text(S.vm, path, text, len);
		if (S.be.free_file)
			S.be.free_file(text);
		if (!ok) {
			S.be.print(DOD_MOHAA_PRINT_ERROR, "mohaa: level script did not start\n");
			Dod_MohaaShutdown();
			return 0;
		}
	}
	S.started = 0;
	return 1;
}

/* the level script's main, once */
static void start_main(void)
{
	if (S.started)
		return;
	S.started = 1;
	if (!ms_exec(S.vm, S.level_script, NULL, NULL, NULL, 0))
		S.be.print(DOD_MOHAA_PRINT_ERROR, "mohaa: level script did not start\n");
}

void Dod_MohaaThink(float now)
{
	ms_value level = ms_nil();
	int i;
	if (!S.vm)
		return;
	S.now = now;
	level.type = MS_LEVEL;
	start_main();
	/* MOHAA level scripts wait for these before touching the world */
	if (S.ticks == 0) {
		S.be.print(DOD_MOHAA_PRINT_CONSOLE, "mohaa: signal prespawn\n");
		ms_notify(S.vm, &level, "prespawn");
	} else if (S.ticks == 1) {
		S.be.print(DOD_MOHAA_PRINT_CONSOLE, "mohaa: signal spawn\n");
		ms_notify(S.vm, &level, "spawn");
	}
	S.ticks++;
	for (i = 0; i < DOD_MOHAA_MAX_MOVERS && S.vm; i++) {
		DodMover *m = &S.movers[i];
		ms_value ent;
		if (!m->id || !m->moving || now < m->end_time)
			continue;
		if (!valid(m->id)) {
			memset(m, 0, sizeof(*m));
			continue;
		}
		if (m->has_dest)
			S.be.set_vec(m->id, DOD_MOHAA_ORIGIN, m->dest);
		if (m->has_angles)
			S.be.set_vec(m->id, DOD_MOHAA_ANGLES, m->angles);
		m->has_dest = m->has_angles = 0;
		m->moving = 0;
		if (m->driving) {
			m->drive_node = next_node(m->drive_node);
			drive_leg(m);
			continue;
		}
		apply_spin(m);
		ent = ms_entity(m->id);
		ms_notify(S.vm, &ent, "movedone");
	}
	if (S.vm)
		ms_frame(S.vm, now);
	if (S.vm)
		cine_think();
}

void Dod_MohaaNotify(uint32_t id, const char *event)
{
	ms_value ent = ms_entity(id);
	if (!S.vm || !id)
		return;
	if (!strcmp(event, "movedone") && route_arrived(id))
		return;	/* a node on the way, not the goal */
	if (!strcmp(event, "death"))
		forget(id);
	ms_notify(S.vm, &ent, event);
}

void Dod_MohaaRunThread(const char *label, uint32_t self)
{
	ms_value me = ms_entity(self);
	if (!S.vm || !label || !*label)
		return;
	if (!ms_exec(S.vm, S.level_script, label, self ? &me : NULL, NULL, 0)) {
		char msg[320];
		snprintf(msg, sizeof(msg), "mohaa: setthread %s: no such label in %s\n", label, S.level_script);
		S.be.print(DOD_MOHAA_PRINT_ERROR, msg);
	}
}

void Dod_MohaaEntityFreed(uint32_t id)
{
	if (!S.vm || !id)
		return;
	forget(id);
	ms_entity_removed(S.vm, id);
}

void Dod_MohaaGetStats(DodMohaaStats *out)
{
	memset(out, 0, sizeof(*out));
	if (!S.vm)
		return;
	out->active = 1;
	out->threads = ms_thread_count(S.vm);
	out->memory = ms_memory_used(S.vm);
	out->memory_peak = ms_memory_peak(S.vm);
	out->errors = ms_error_count(S.vm);
	out->unknown_commands = S.nunknown;
}
