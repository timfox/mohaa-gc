#ifndef DODGC_DOD_MOHAA_H
#define DODGC_DOD_MOHAA_H

/*
 * MOHAA mission scripts (.scr) on DoD-GC.
 *
 * A map that ships maps/<map>.scr gets its script run by the MOHAA script VM
 * (src/mohaa/, MIT, from timfox/mohaa-gc). This file binds the VM's commands
 * to GoldSrc entities through a small backend table, so the binding logic is
 * plain C and testable on a PC; dod_mohaa_ents.cpp fills the table from the
 * HL1SDK game DLL. Maps without a .scr cost nothing: no VM is created.
 *
 * MOHAA units are larger than GoldSrc's (player 94 vs 72 tall); positions are
 * scaled by DOD_MOHAA_SCALE on the way in and out, the same factor the map
 * converter uses. Angles are not scaled.
 */

#include <stddef.h>
#include <stdint.h>
#include "dod_mohaa_hud.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOD_MOHAA_SCALE (72.0f / 94.0f)
#define DOD_MOHAA_MAX_MOVERS 64

enum { DOD_MOHAA_ORIGIN = 0, DOD_MOHAA_ANGLES = 1 };
enum { DOD_MOHAA_TARGETNAME = 0, DOD_MOHAA_CLASSNAME = 1, DOD_MOHAA_MODEL = 2, DOD_MOHAA_TARGET = 3 };
/* set_flag modes: hide, solidity, and whether damage can affect this entity. */
enum { DOD_MOHAA_HIDDEN = 0, DOD_MOHAA_NOTSOLID = 1, DOD_MOHAA_TAKEDAMAGE = 2 };
/* Sound channels, from the ubersound alias's channel name. */
enum { DOD_MOHAA_CHAN_AUTO = 0, DOD_MOHAA_CHAN_VOICE, DOD_MOHAA_CHAN_ITEM, DOD_MOHAA_CHAN_BODY, DOD_MOHAA_CHAN_WEAPON };
/* Sound aliases come from maps/<map>.snd, written by mohaa-gc tools/ubersound.py (lines "alias sample volume mindist
   channel"; repeated aliases are variants picked at random). At most this many rows are kept. */
#define DOD_MOHAA_MAX_SOUNDS 256
/* Orders to a script actor (a MOHAA AI soldier, played by a grunt). pos is in GoldSrc units. */
enum {
	DOD_MOHAA_AI_ON = 0, DOD_MOHAA_AI_OFF, DOD_MOHAA_ATTACK,	/* attackplayer */
	DOD_MOHAA_WALKTO, DOD_MOHAA_RUNTO, DOD_MOHAA_TURNTO, DOD_MOHAA_STOP
};
/* HUD parts a cutscene hides: ALL is MOHAA's "drawhud 0"; WEAPON (crosshair, ammo, view model) goes while the
   player is locked into a scripted ride. */
enum { DOD_MOHAA_HUD_ALL = 1, DOD_MOHAA_HUD_WEAPON = 2 };
enum { DOD_MOHAA_PRINT_CONSOLE = 0, DOD_MOHAA_PRINT_HUD = 1, DOD_MOHAA_PRINT_CENTER = 2, DOD_MOHAA_PRINT_ERROR = 3 };

/* Entity ids are opaque to this file: the backend packs edict index and serial so a
 * removed-and-reused edict never answers for an old reference. 0 is never valid. */
#define DOD_MOHAA_NODE_ID 0x80000000u	/* entity ids from the backend keep this bit clear */

typedef struct DodMohaaBackend {
	char *(*load_file)(const char *path, size_t *len);  /* NULL if missing */
	void (*free_file)(char *text);
	void (*print)(int channel, const char *text);
	int (*find)(const char *targetname, uint32_t *ids, int max);  /* returns total matches */
	int (*valid)(uint32_t id);
	void (*get_vec)(uint32_t id, int what, float out[3]);         /* GoldSrc units */
	void (*set_vec)(uint32_t id, int what, const float v[3]);
	float (*get_health)(uint32_t id);
	void (*set_health)(uint32_t id, float health);
	const char *(*get_str)(uint32_t id, int what);
	void (*set_targetname)(uint32_t id, const char *name);
	void (*set_flag)(uint32_t id, int flag, int on);
	void (*remove)(uint32_t id);
	void (*set_velocity)(uint32_t id, const float vel[3], const float avel[3]);
	void (*use_targets)(const char *targetname);                 /* "trigger $name" */
	uint32_t (*spawn)(const char *classname, const char *const *keys, const char *const *values, int count);
	/* Play a sample (relative to sound/, e.g. "mohaa/mechanics/door_01.wav") on an entity. loop 1 plays it on the
	   static channel (the wav's own loop marker repeats it), loop -1 stops that sample. attn is GoldSrc attenuation. */
	void (*sound)(uint32_t id, const char *sample, int loop, float volume, float attn, int channel);
	/* At level start, for each sample maps/<map>.snd names. NULL: nothing to precache (host tests). */
	void (*precache_sound)(const char *sample);
	/* Scripted TIKI models baked to GoldSrc MDL by tools/mohaa_tiki_model.py. Models are precached
	   from maps/<map>.models at ServerActivate, before the level script's first frame. */
	int (*precache_model)(const char *model);
	/* Set a script_model/script_object to its already-preloaded GoldSrc model. 0 when this TIKI was
	   not baked/staged for the map; tag sampling still works without a drawable mesh. */
	int (*set_model)(uint32_t id, const char *tiki);
	/* Select a named exported sequence on an already-bound script model. */
	int (*set_animation)(uint32_t id, const char *alias);
	/* An order to an actor; returns 0 when id is not one. The game sends "movedone" when a walk/run
	   order arrives and "death" when the actor dies, through Dod_MohaaNotify. NULL: no actors. */
	int (*actor)(uint32_t id, int order, const float pos[3]);
	/* Path nodes (maps/<map>.nodes, see dod_mohaa_paths.h) are linked at level start where this says a soldier can walk
	   from a to b (feet origins). A script sees a node as an entity with id DOD_MOHAA_NODE_ID | index, which the
	   backend never hands out. NULL: nodes are loaded for names but not linked, so move orders go straight. */
	int (*walkable)(const float a[3], const float b[3]);
	/* getcvar: a cvar's string, "" when unknown. NULL: always "". */
	const char *(*get_cvar)(const char *name);
	/* setcvar: set a cvar. NULL: ignored. */
	void (*set_cvar)(const char *name, const char *value);
	/* fadeout/fadein: fade every player's screen over seconds to (or from) colour r g b (0..1) at alpha. */
	void (*fade)(float seconds, float r, float g, float b, float alpha, int out);
	/* Background music for every player (late joiners too): intro plays once, then loop repeats; loop "" plays
	   intro once and stops; intro NULL stops the music. Paths are game-relative ("sound/mohaa/music/x.wav"),
	   PCM wavs written by mohaa-gc tools/music.py. NULL: no music. */
	void (*music)(const char *intro, const char *loop);
	/* In-game cutscenes (see "Cutscenes" in dod_mohaa.c). All NULL-safe: a backend without them plays the script
	   with the player free. */
	/* physics_off / freezeplayer: the player stops moving under their own control (they can still look) */
	void (*player_lock)(uint32_t id, int locked);
	/* Put the player at pos (GoldSrc units): pos is where their eyes go when eye is 1, their feet when 0. */
	void (*place_player)(uint32_t id, const float pos[3], int eye);
	/* Turn the player's view: to angles when add is 0, by angles[1] degrees of yaw when 1 (their own look stays). */
	void (*view)(uint32_t id, const float angles[3], int add);
	/* What of every player's HUD to hide: DOD_MOHAA_HUD_* bits, 0 shows it all. */
	void (*hud)(int hide);
	/* Scripted huddraw elements and the current objective compass target. NULL: no custom HUD. */
	void (*hud_draw)(int index, const DodMohaaHudDraw *draw);
	void (*compass_target)(const float target[3], int visible);
	/* A shot or blast at point (GoldSrc units): damage what is within radius and fire MOHAA damage triggers
	   (converted with spawnflags 2, no touch) whose box holds the point. attacker 0: the world. */
	void (*damage_at)(uint32_t attacker, const float point[3], float radius, float damage);
	void *(*alloc)(void *ptr, size_t old_size, size_t new_size); /* NULL: pool below, else malloc */
	/* A region the VM allocates from when alloc is NULL (dod_mohaa_pool.h), instead of the engine heap. It must
	   stay valid until the next Dod_MohaaLevelInit or Dod_MohaaShutdown, or until Dod_MohaaDropPool says it is
	   gone. NULL: malloc. */
	void *pool;
	size_t pool_size;
	/* more regions for the same pool, when no single gap held it all (0 size: unused) */
	void *pool_more[7];
	size_t pool_more_size[7];
} DodMohaaBackend;

typedef struct DodMohaaStats {
	int active;            /* a VM is running for this map */
	int threads;
	size_t memory, memory_peak;
	int errors;
	int unknown_commands;  /* distinct command names nothing handles yet */
} DodMohaaStats;

/* Start the map's script if maps/<mapname>.scr exists. Replaces any previous map's VM.
 * memory_budget 0 means unlimited. Returns 1 when a script is running. */
int Dod_MohaaLevelInit(const DodMohaaBackend *backend, const char *mapname, float now, size_t memory_budget);
/* Called from ServerActivate, after map entities spawn but before runtime. */
void Dod_MohaaPrecacheModels(void);
/* Every server frame: sends "prespawn" then "spawn" to level, runs threads, finishes moves. */
void Dod_MohaaThink(float now);
void Dod_MohaaShutdown(void);
/* A map entity's key that only scripts read (MOHAA "#set", "#group", ...): the script sees it as $ent.set (MOHAA drops the '#').
 * Numbers become numbers. Ignored when no script runs. */
void Dod_MohaaEntityKey(uint32_t id, const char *key, const char *value);
/* The backend replaced entity from with to (a mohaa_actor placeholder became a grunt): to keeps from's script
 * variables, map keys included. from may be an id no entity has, to park them meanwhile. */
void Dod_MohaaEntityMoved(uint32_t from, uint32_t to);
/* Who set off the event about to be notified (a trigger's activator): scripts read it as parm.other. 0: NULL. */
void Dod_MohaaSetOther(uint32_t id);
/* The backend's pool region is being taken back (GameCube: the map arena resets at map change): stop the
 * script and forget everything in the region without touching it. Does nothing when no pool is in use. */
void Dod_MohaaDropPool(void);
/* Game events: Dod_MohaaNotify(id, "trigger") wakes "$t waittill trigger". */
void Dod_MohaaNotify(uint32_t id, const char *event);
void Dod_MohaaEntityFreed(uint32_t id);
/* A trigger with MOHAA's setthread fired: run that label of the level script with self = the trigger. */
void Dod_MohaaRunThread(const char *label, uint32_t self);
void Dod_MohaaGetStats(DodMohaaStats *out);
/* Path nodes this level loaded and linked (0 when none). */
int Dod_MohaaPathNodes(int *links);

#ifdef __cplusplus
}
#endif

#endif
