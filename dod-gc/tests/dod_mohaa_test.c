/* MOHAA script binding (dod_mohaa.c) against a mock GoldSrc world. */
#define _POSIX_C_SOURCE 200809L
#include "dod_mohaa.h"
#include "dod_mohaa_pool.h"

#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Ent {
	int alive;
	char targetname[32], classname[32], target[32];
	float origin[3], angles[3], vel[3], avel[3];
	float health;
	int hidden, notsolid, used, serial;
	char sound[64];
} Ent;

#define NENTS 16
static Ent ents[NENTS];
static const char *files[8][2];
static char log_buf[4096];

static void logf_(const char *s)
{
	strncat(log_buf, s, sizeof(log_buf) - strlen(log_buf) - 1);
}

/* ids carry a serial so a reused slot does not answer for an old reference */
static uint32_t make_id(int i) { return (uint32_t)(i + 1) | ((uint32_t)ents[i].serial << 8); }
static Ent *ent(uint32_t id)
{
	int i = (int)(id & 0xff) - 1;
	if (i < 0 || i >= NENTS || !ents[i].alive || ents[i].serial != (int)(id >> 8))
		return NULL;
	return &ents[i];
}

static char *m_load(const char *path, size_t *len)
{
	int i;
	for (i = 0; i < 8 && files[i][0]; i++) {
		if (!strcmp(files[i][0], path)) {
			char *s = strdup(files[i][1]);
			*len = strlen(s);
			return s;
		}
	}
	return NULL;
}
static void m_free(char *t) { free(t); }
static void m_print(int ch, const char *t)
{
	static const char *p[] = {"", "[hud] ", "[center] ", "[error] "};
	logf_(p[ch]);
	logf_(t);
	if (ch == DOD_MOHAA_PRINT_CENTER)
		logf_("\n");
}
static int m_find(const char *name, uint32_t *ids, int max)
{
	int i, n = 0;
	for (i = 0; i < NENTS; i++)
		if (ents[i].alive && !strcmp(ents[i].targetname, name)) {
			if (n < max)
				ids[n] = make_id(i);
			n++;
		}
	return n;
}
static int m_valid(uint32_t id) { return ent(id) != NULL; }
static void m_get_vec(uint32_t id, int what, float out[3]) { memcpy(out, what ? ent(id)->angles : ent(id)->origin, 12); }
static void m_set_vec(uint32_t id, int what, const float v[3]) { memcpy(what ? ent(id)->angles : ent(id)->origin, v, 12); }
static float m_get_health(uint32_t id) { return ent(id)->health; }
static void m_set_health(uint32_t id, float h) { ent(id)->health = h; }
static const char *m_get_str(uint32_t id, int what)
{
	return what == DOD_MOHAA_TARGETNAME ? ent(id)->targetname : what == DOD_MOHAA_TARGET ? ent(id)->target : ent(id)->classname;
}
static void m_set_tn(uint32_t id, const char *n) { snprintf(ent(id)->targetname, 32, "%s", n); }
static void m_set_flag(uint32_t id, int f, int on) { if (f == DOD_MOHAA_HIDDEN) ent(id)->hidden = on; else ent(id)->notsolid = on; }
static void m_remove(uint32_t id) { ent(id)->alive = 0; }
static void m_set_vel(uint32_t id, const float v[3], const float a[3]) { memcpy(ent(id)->vel, v, 12); memcpy(ent(id)->avel, a, 12); }
static void m_use(const char *tn)
{
	int i;
	for (i = 0; i < NENTS; i++)
		if (ents[i].alive && !strcmp(ents[i].targetname, tn))
			ents[i].used++;
}
static int add(const char *tn, const char *cls, float x, float y, float z)
{
	int i;
	for (i = 0; i < NENTS; i++)
		if (!ents[i].alive) {
			int serial = ents[i].serial + 1;
			memset(&ents[i], 0, sizeof(Ent));
			ents[i].serial = serial;
			ents[i].alive = 1;
			snprintf(ents[i].targetname, 32, "%s", tn);
			snprintf(ents[i].classname, 32, "%s", cls);
			ents[i].origin[0] = x;
			ents[i].origin[1] = y;
			ents[i].origin[2] = z;
			ents[i].health = 100;
			return i;
		}
	return -1;
}
static uint32_t m_spawn(const char *cls, const char *const *k, const char *const *v, int n)
{
	int i = add("", cls, 0, 0, 0), j;
	for (j = 0; j < n; j++) {
		if (!strcmp(k[j], "targetname"))
			snprintf(ents[i].targetname, 32, "%s", v[j]);
		else if (!strcmp(k[j], "origin"))
			sscanf(v[j], "%f %f %f", &ents[i].origin[0], &ents[i].origin[1], &ents[i].origin[2]);
	}
	return make_id(i);
}
static char precached[512];
static void m_sound(uint32_t id, const char *s, int loop, float vol, float attn, int chan)
{
	char line[160];
	snprintf(ent(id)->sound, 64, "%s%s", loop > 0 ? "loop:" : (loop < 0 ? "stop:" : ""), s);
	snprintf(line, sizeof(line), "<sound %s %s %d %.2f %.2f %d>\n", ent(id)->targetname, s, loop, vol, attn, chan);
	logf_(line);
}
static void m_precache(const char *s)
{
	if (strlen(precached) + strlen(s) + 2 > sizeof(precached))
		return;
	strcat(precached, s);
	strcat(precached, ";");
}

/* actors: classname "actor" in the mock; orders are logged */
/* a wall along x = 0 from y = -50 to 150: only round its far end (y > 150) can a soldier cross */
static int walk_tests;
static int m_walkable(const float a[3], const float b[3])
{
	walk_tests++;
	if ((a[0] < 0) == (b[0] < 0))
		return 1;
	{
		const float t = (0 - a[0]) / (b[0] - a[0]), y = a[1] + t * (b[1] - a[1]);
		return y > 150.0f || y < -50.0f;
	}
}

static const char *m_get_cvar(const char *name) { return strcmp(name, "skill") ? "" : "2"; }

static char cvar_set[64];
static void m_set_cvar(const char *name, const char *value) { snprintf(cvar_set, sizeof(cvar_set), "%s=%s", name, value); }

static void m_fade(float t, float r, float g, float b, float a, int out)
{
	char line[96];
	snprintf(line, sizeof(line), "<fade%s %.1f %.1f %.1f %.1f %.1f>\n", out ? "out" : "in", t, r, g, b, a);
	logf_(line);
}

static int m_actor(uint32_t id, int order, const float pos[3])
{
	static const char *names[] = {"ai_on", "ai_off", "attack", "walkto", "runto", "turnto", "stop"};
	char line[96];
	Ent *e = ent(id);
	if (!e || strcmp(e->classname, "actor"))
		return 0;
	snprintf(line, sizeof(line), "<%s %s %.1f %.1f %.1f>\n", e->targetname, names[order], pos[0], pos[1], pos[2]);
	logf_(line);
	return 1;
}

static void m_music(const char *intro, const char *loop)
{
	char buf[256];
	if (!intro)
		snprintf(buf, sizeof(buf), "<music off>\n");
	else
		snprintf(buf, sizeof(buf), "<music %s | %s>\n", intro, loop);
	logf_(buf);
}

static DodMohaaBackend backend(void)
{
	DodMohaaBackend b;
	memset(&b, 0, sizeof(b));
	b.load_file = m_load;
	b.free_file = m_free;
	b.print = m_print;
	b.find = m_find;
	b.valid = m_valid;
	b.get_vec = m_get_vec;
	b.set_vec = m_set_vec;
	b.get_health = m_get_health;
	b.set_health = m_set_health;
	b.get_str = m_get_str;
	b.set_targetname = m_set_tn;
	b.set_flag = m_set_flag;
	b.remove = m_remove;
	b.set_velocity = m_set_vel;
	b.use_targets = m_use;
	b.spawn = m_spawn;
	b.sound = m_sound;
	b.actor = m_actor;
	b.walkable = m_walkable;
	b.get_cvar = m_get_cvar;
	b.fade = m_fade;
	b.set_cvar = m_set_cvar;
	b.precache_sound = m_precache;
	b.music = m_music;
	return b;
}

static void reset(void)
{
	Dod_MohaaShutdown();
	memset(ents, 0, sizeof(ents));
	memset(files, 0, sizeof(files));
	log_buf[0] = 0;
	precached[0] = 0;
}

static int near(float a, float b) { return fabsf(a - b) < 0.01f; }

static void run(float from, float to)
{
	float t;
	for (t = from; t <= to + 0.0001f; t += 0.05f)
		Dod_MohaaThink(t);
}

static void test_no_script_no_vm(void)
{
	DodMohaaBackend b = backend();
	DodMohaaStats st;
	reset();
	assert(!Dod_MohaaLevelInit(&b, "dod_avalanche", 0, 0));
	Dod_MohaaThink(1.0f);
	Dod_MohaaGetStats(&st);
	assert(!st.active && st.memory == 0);
}

static void test_level_flow_and_movers(void)
{
	DodMohaaBackend b = backend();
	DodMohaaStats st;
	int door, wall, trig;
	reset();
	door = add("door1", "func_wall", 0, 0, 0);
	wall = add("wall", "func_wall", 10, 0, 0);
	trig = add("relay", "trigger_relay", 0, 0, 0);
	files[0][0] = "maps/m1l1.scr";
	files[0][1] =
		"main:\n"
		"\tlevel waittill prespawn\n"
		"\t$wall hide\n"
		"\t$wall notsolid\n"
		"\tlevel waittill spawn\n"
		"\tprintln \"spawned\"\n"
		"\t$door1 time 2\n"
		"\t$door1 moveto (0 0 94)\n"   /* 94 MOHAA units = 72 GoldSrc */
		"\t$door1 playsound door_open\n"
		"\t$door1 waitmove\n"
		"\tprintln \"door at \" $door1.origin\n"
		"\ttrigger $relay\n"
		"\tlocal.e = spawn script_model targetname crate origin (94 0 0)\n"
		"\tprintln \"crate \" local.e.targetname\n"
		"\t$door1 moveUp 94\n"
		"\t$door1 time 0\n"
		"\t$door1 move\n"
		"\tiprintln \"objective\"\n"
		"\tcenterprint \"go\"\n"
		"\t$door1 unboundcommand 1\n"
		"\t$door1 unboundcommand 2\n"
		"\t$wall remove\n"
		"\tprintln \"wall gone \" ($wall == NULL)\n"
		"end\n";
	assert(Dod_MohaaLevelInit(&b, "m1l1", 0, 256 * 1024));
	Dod_MohaaThink(0.05f);                      /* prespawn */
	assert(ents[wall].hidden && ents[wall].notsolid);
	Dod_MohaaThink(0.10f);                      /* spawn: the move starts */
	assert(strstr(log_buf, "spawned"));
	assert(near(ents[door].vel[2], 36.0f));     /* 72 GoldSrc units over 2 s */
	assert(!ents[door].sound[0]);	/* no maps/m1l1.snd: aliases play nothing (and are reported) */
	assert(strstr(log_buf, "sound 'door_open' is not in this map's sound table"));
	run(0.15f, 2.0f);
	assert(!strstr(log_buf, "door at"));
	run(2.05f, 2.3f);
	assert(strstr(log_buf, "door at (0.000 0.000 94.000)"));
	assert(near(ents[door].vel[2], 0.0f));
	assert(ents[trig].used == 1);
	assert(strstr(log_buf, "crate crate"));
	assert(near(ents[door].origin[2], 144.0f)); /* moveUp 94 with time 0 snaps */
	assert(strstr(log_buf, "[hud] objective"));
	assert(strstr(log_buf, "[center] go"));
	assert(strstr(log_buf, "wall gone 1"));
	assert(!ents[wall].alive);
	Dod_MohaaGetStats(&st);
	assert(st.active && st.errors == 0 && st.unknown_commands == 1);
	assert(st.memory_peak < 64 * 1024);
	/* the unbound command was reported once, not twice */
	assert(strstr(log_buf, "'unboundcommand'") == strrchr(log_buf, '\'') - strlen("'unboundcommand"));
}

static void test_waittill_trigger_and_freed(void)
{
	DodMohaaBackend b = backend();
	int t;
	reset();
	t = add("trig", "trigger_multiple", 0, 0, 0);
	add("guard", "monster", 0, 0, 0);
	files[0][0] = "maps/t.scr";
	files[0][1] =
		"main:\n"
		"\t$guard thread watch\n"
		"\t$trig waittill trigger\n"
		"\tprintln \"hit\"\n"
		"end\n"
		"watch:\n"
		"\tself waittill removed\n"
		"\tprintln \"guard removed\"\n"
		"end\n";
	assert(Dod_MohaaLevelInit(&b, "t", 0, 0));
	run(0.05f, 0.5f);
	assert(!strstr(log_buf, "hit"));
	Dod_MohaaNotify(make_id(t), "trigger");
	assert(strstr(log_buf, "hit"));
	ents[1].alive = 0;
	Dod_MohaaEntityFreed(make_id(1));
	assert(strstr(log_buf, "guard removed"));
}

static void test_budget_refuses_cleanly(void)
{
	DodMohaaBackend b = backend();
	reset();
	files[0][0] = "maps/big.scr";
	files[0][1] = "main:\n\tprintln \"hi\"\nend\n";
	assert(!Dod_MohaaLevelInit(&b, "big", 0, 512));   /* far too small to compile */
	assert(strstr(log_buf, "[error]"));
	/* a big global that does not fit later: the error says how full the budget was */
	{
		static char big[64 * 1024];
		size_t o = 0;
		int i;
		o += (size_t)snprintf(big + o, sizeof(big) - o, "main:\n");
		for (i = 0; o + 64 < sizeof(big); i++)
			o += (size_t)snprintf(big + o, sizeof(big) - o, "\tlocal.v%d = \"string number %d\"\n", i, i);
		snprintf(big + o, sizeof(big) - o, "end\n");
		reset();
		files[0][0] = "maps/fit.scr";
		files[0][1] = "main:\n\texec global/big.scr\nend\n";
		files[1][0] = "global/big.scr";
		files[1][1] = big;
		assert(Dod_MohaaLevelInit(&b, "fit", 0, 48 * 1024));
		run(0.05f, 0.2f);
		assert(strstr(log_buf, "out of memory"));
		assert(strstr(log_buf, "mohaa: script memory ") && strstr(log_buf, "budget 48 KB\n"));
	}
}

static void test_actors(void)
{
	DodMohaaBackend b = backend();
	int guy;
	b.walkable = NULL;	/* nodes known by name only: every order goes straight */
	reset();
	files[1][0] = "maps/a.nodes";
	files[1][1] = "# x y z grav spawnflags targetname\n500 500 0 0 0 -\n10 20 30 0 0 path7\n";
	guy = add("guy", "actor", 0, 0, 0);
	add("node1", "info_pathnode", 72, 0, 0);
	add("crate", "func_wall", 0, 0, 0);
	files[0][0] = "maps/a.scr";
	files[0][1] =
		"main:\n"
		"\t$guy ai_off\n"
		"\t$guy runto $node1\n"
		"\t$guy waittill movedone\n"
		"\tprintln \"arrived\"\n"
		"\t$guy walkto \"node1\"\n"
		"\t$guy walkto (0 94 0)\n"
		"\t$guy turnto $crate\n"
		"\t$guy runto $path7\n"
		"\t$guy walkto \"path7\"\n"
		"\tprintln $path7.origin\n"
		"\t$guy runto $nowhere\n"
		"\t$guy ai_on\n"
		"\t$guy attackplayer\n"
		"\t$guy waittill death\n"
		"\tprintln \"guy died\"\n"
		"\t$crate ai_on\n"
		"end\n";
	assert(Dod_MohaaLevelInit(&b, "a", 0, 0));
	run(0.05f, 0.3f);
	assert(strstr(log_buf, "<guy ai_off 0.0 0.0 0.0>\n<guy runto 72.0 0.0 0.0>\n"));
	assert(!strstr(log_buf, "arrived"));
	Dod_MohaaNotify(make_id(guy), "movedone");
	run(0.35f, 0.5f);
	assert(strstr(log_buf, "arrived\n<guy walkto 72.0 0.0 0.0>\n<guy walkto 0.0 72.0 0.0>\n<guy turnto 0.0 0.0 0.0>\n"
		"<guy runto 10.0 20.0 30.0>\n<guy walkto 10.0 20.0 30.0>\n"));
	assert(strstr(log_buf, "<guy ai_on 0.0 0.0 0.0>\n<guy attack 0.0 0.0 0.0>\n"));
	assert(strstr(log_buf, "(13.056 26.111 39.167)\n"));	/* $path7.origin, back in MOHAA units */
	assert(strstr(log_buf, "runto needs a vector, an entity or a node name"));	/* $nowhere */
	Dod_MohaaNotify(make_id(guy), "death");
	run(0.55f, 0.7f);
	assert(strstr(log_buf, "guy died"));
	assert(strstr(log_buf, "ai_on: not an actor"));	/* a func_wall is no soldier: reported, script goes on */
}

static void test_sounds(void)
{
	DodMohaaBackend b = backend();
	int door, i, a = 0, bb = 0;
	reset();
	door = add("door", "func_door", 0, 0, 0);
	add("siren", "info_target", 0, 0, 0);
	files[0][0] = "maps/s.scr";
	files[0][1] =
		"main:\n"
		"\t$door playsound door_open\n"
		"\t$siren loopsound alarm\n"
		"\t$siren loopsound alarm\n"     /* replaces, does not stack */
		"\twait 1\n"
		"\t$siren stoploopsound\n"
		"\t$door playsound no_such_alias\n"
		"\t$door playsound no_such_alias\n"
		"end\n";
	files[1][0] = "maps/s.snd";
	files[1][1] =
		"# alias sample volume mindist channel\n"
		"door_open mohaa/door_01.wav 0.80 160 auto\n"
		"door_open mohaa/door_02.wav 0.70 320 item\n"
		"alarm mohaa/alarm.wav 1.00 600 voice\n"
		"DOOR_SHUT mohaa/door_01.wav 0.5 64 body\n";
	assert(Dod_MohaaLevelInit(&b, "s", 0, 0));
	/* each sample precached once, even when two aliases share it */
	assert(!strcmp(precached, "mohaa/door_01.wav;mohaa/door_02.wav;mohaa/alarm.wav;"));
	Dod_MohaaThink(0.0f);   /* main runs on the first frame */
	assert(strstr(log_buf, "<sound door mohaa/door_0"));
	assert(strstr(log_buf, "<sound siren mohaa/alarm.wav 1 1.00 0.25 1>\n"
		"<sound siren mohaa/alarm.wav -1 0.00 0.00 0>\n<sound siren mohaa/alarm.wav 1 1.00 0.25 1>\n"));
	run(0.05f, 1.3f);
	assert(strstr(log_buf, "<sound siren mohaa/alarm.wav -1"));
	assert(strstr(ents[1].sound, "stop:mohaa/alarm.wav"));
	/* an unknown alias is reported once and plays nothing */
	{
		const char *msg = "sound 'no_such_alias' is not in this map's sound table";
		const char *p = strstr(log_buf, msg);
		assert(p && !strstr(p + strlen(msg), "no_such_alias"));
	}
	/* variants: both door sounds come up, with their own volume and attenuation (160 -> 0.80, 320 -> 0.40) */
	for (i = 0; i < 40; i++) {
		log_buf[0] = 0;
		precached[0] = 0;
		Dod_MohaaShutdown();
		files[0][1] = "main:\n\t$door playsound door_open\n\t$door playsound DOOR_SHUT\nend\n";
		assert(Dod_MohaaLevelInit(&b, "s", (float)i, 0));
		Dod_MohaaThink((float)i);
		a += strstr(log_buf, "mohaa/door_01.wav 0 0.80 0.80 0") != NULL;
		bb += strstr(log_buf, "mohaa/door_02.wav 0 0.70 0.40 2") != NULL;
		assert(strstr(log_buf, "mohaa/door_01.wav 0 0.50 2.00 3"));   /* case-insensitive alias */
	}
	assert(a > 0 && bb > 0 && a + bb == 40);
	(void)door;
}

static void test_music(void)
{
	DodMohaaBackend b = backend();
	reset();
	add("player", "player", 0, 0, 0);
	files[0][0] = "maps/m.scr";
	files[0][1] =
		"main:\n"
		"\twait 0.1\n"
		"\tforcemusic aux1 normal\n"
		"\t$player stufftext \"tmstartloop sound/music/MUS_Tank.mp3\"\n"
		"\t$player stufftext \"tmstop; tmstart sound/music/mus_win.mp3; say hi\"\n"
		"\tsoundtrack music/other.mus\n"
		"\tforcemusic aux9\n"
		"\tsoundtrack music/none.mus\n"
		"end\n";
	files[1][0] = "music/m.mood";
	files[1][1] =
		"# mood sample volume loop fadetime\n"
		"normal mohaa/music/calm.wav 0.70 1 0.0\n"
		"aux1 mohaa/music/fight.wav 1.00 0 1.5\n";
	files[2][0] = "music/other.mood";
	files[2][1] = "normal mohaa/music/other.wav 1.00 1 0.0\n";
	assert(Dod_MohaaLevelInit(&b, "m", 0, 0));
	/* the map's own soundtrack starts on normal */
	assert(!strncmp(log_buf, "<music sound/mohaa/music/calm.wav | sound/mohaa/music/calm.wav>\n", 62));
	run(0.05f, 0.3f);
	assert(strstr(log_buf,
		"<music sound/mohaa/music/fight.wav | sound/mohaa/music/calm.wav>\n"	/* once, then back to normal */
		"<music sound/mohaa/music/mus_tank.wav | sound/mohaa/music/mus_tank.wav>\n"
		"<music sound/mohaa/music/fight.wav | sound/mohaa/music/calm.wav>\n"	/* tmstop */
		"<music sound/mohaa/music/mus_win.wav | sound/mohaa/music/calm.wav>\n"
		"<music sound/mohaa/music/other.wav | sound/mohaa/music/other.wav>\n"));
	assert(strstr(log_buf, "no mood aux9"));
	assert(strstr(log_buf, "no music/none.mood, the level plays without music"));
	/* no table: nothing plays and nothing is reported */
	reset();
	files[0][0] = "maps/q.scr";
	files[0][1] = "main:\n\tforcemusic aux1\nend\n";
	assert(Dod_MohaaLevelInit(&b, "q", 0, 0));
	run(0.05f, 0.1f);
	assert(!strstr(log_buf, "music") && !strstr(log_buf, "error"));
}

static void test_routes(void)
{
	DodMohaaBackend b = backend();
	int guy;
	reset();
	walk_tests = 0;
	guy = add("guy", "actor", -120, 0, 36);	/* a grunt's origin is its body centre, 36 over its feet */
	add("spot", "info_target", 150, 0, 0);
	files[0][0] = "maps/r.scr";
	files[0][1] =
		"main:\n"
		"\t$guy runto $spot\n"
		"\t$guy waittill movedone\n"
		"\tprintln \"arrived\"\n"
		"\tlocal.a = isalive $guy\n"
		"\tlocal.d = isalive $nobody\n"
		"\tprintln (\"alive \" + local.a + \" \" + local.d + \" skill \" + (getcvar \"skill\") + \"|\" + (getcvar \"nope\") + \"|\")\n"
		"\tfadeout 2 0 0 0 1\n"
		"\tfadein 0.5 1 1 1\n"
		"\tprintln (\"node set \" + ($west.set * 2) + \" note \" + $west.note + \"|\")\n"
		"end\n";
	files[1][0] = "maps/r.nodes";
	files[1][1] =
		"# x y z grav spawnflags targetname\n"
		"-100 0 0 0 0 west #set=3 #note=a%20b%25 stray\n"
		"-100 250 0 0 0 -\n"
		"100 250 0 0 0 -\n"
		"100 0 0 0 0 east\n";
	assert(Dod_MohaaLevelInit(&b, "r", 0, 0));
	assert(strstr(log_buf, "mohaa: 4 path nodes from maps/r.nodes, 3 links"));
	assert(walk_tests > 0);
	run(0.05f, 0.2f);
	assert(strstr(log_buf, "<guy runto -100.0 0.0 0.0>\nmohaa: runto over 4 path nodes\n"));
	/* each node reached orders the next leg, unheard by the script; the goal's arrival wakes it */
	Dod_MohaaNotify(make_id(guy), "movedone");
	Dod_MohaaNotify(make_id(guy), "movedone");
	Dod_MohaaNotify(make_id(guy), "movedone");
	run(0.25f, 0.4f);
	assert(strstr(log_buf, "<guy runto -100.0 250.0 0.0>\n<guy runto 100.0 250.0 0.0>\n<guy runto 100.0 0.0 0.0>\n"));
	assert(!strstr(log_buf, "arrived"));
	Dod_MohaaNotify(make_id(guy), "movedone");
	run(0.45f, 0.6f);
	assert(strstr(log_buf, "<guy runto 150.0 0.0 0.0>\n"));
	assert(!strstr(log_buf, "arrived"));
	Dod_MohaaNotify(make_id(guy), "movedone");
	run(0.65f, 0.8f);
	assert(strstr(log_buf, "arrived\nalive 1 0 skill 2||\n<fadeout 2.0 0.0 0.0 0.0 1.0>\n<fadein 0.5 1.0 1.0 1.0 1.0>\nnode set 6 note a b%|\n"));
	{
		int links = 0;
		assert(Dod_MohaaPathNodes(&links) == 4 && links == 3);
	}
}

static void test_setthread_and_quiet_commands(void)
{
	DodMohaaBackend b = backend();
	int t;
	reset();
	t = add("t_gate", "trigger_multiple", 0, 0, 0);
	ents[t].angles[1] = 90.0f;   /* facing +y */
	strcpy(ents[t].target, "dest");
	files[0][0] = "maps/g.scr";
	files[0][1] =
		"main:\n"
		"\t$t_gate lighton\n"
		"\t$t_gate light 1 0.5 0.5 200\n"
		"\t$t_gate lightradius 200\n"
		"\t$t_gate disconnect_paths\n"
		"\t$t_gate holster\n"
		"\t$t_gate anim idle\n"
		"\tprintln (\"tag \" + ($t_gate gettagposition \"tag_barrel\"))\n"
		"\t$t_gate velocity (94 0 0)\n"
		"\tsetcvar \"g_mohaa\" \"1\"\n"
		"\taddobjective 1 1 \"Find the radio\" $t_gate\n"
		"\tsetcurrentobjective 1\n"
		"\texec global/nothere.scr\n"
		"\tlocal.d = spawn script_origin \"#set\" \"4\" targetname dest\n"
		"\tprintln (\"spawned set \" + local.d.set)\n"
		"\tlocal.gun = $t_gate queryturretslotentity 0\n"
		"\tlocal.gun setaimtarget $t_gate\n"
		"\tprintln (\"turret \" + local.gun.targetname)\n"
		"\tlocal.p = $t_gate.forwardvector * 128 + $t_gate.origin\n"
		"\tprintln (\"ahead \" + local.p)\n"
		"\tprintln (\"left \" + $t_gate.leftvector + \" up \" + $t_gate.upvector)\n"
		"end\n"
		"gate_open:\n"
		"\tprintln (\"gate by \" + self.targetname)\n"
		"\tprintln (\"set \" + (self.set + 1) + \" group \" + self.group)\n"
		"\tif (parm.other == NULL) println \"other none\"\n"
		"\telse println (\"other \" + parm.other.targetname)\n"
		"\t$t_gate runto $t_gate\n"
		"\tprintln (\"target \" + self.target + \" \" + $dest.target)\n"
		"end\n";
	assert(Dod_MohaaLevelInit(&b, "g", 0, 0));
	Dod_MohaaEntityKey(make_id(t), "#set", "3");   /* map keys arrive as the map's entities spawn, after the VM starts */
	Dod_MohaaEntityKey(make_id(t), "#group", "left side");
	run(0.05f, 0.2f);
	Dod_MohaaSetOther(make_id(t));   /* the trigger's activator */
	Dod_MohaaRunThread("gate_open", make_id(t));
	Dod_MohaaSetOther(0);
	Dod_MohaaRunThread("gate_open", make_id(t));
	Dod_MohaaRunThread("no_label", make_id(t));
	run(0.25f, 0.3f);
	assert(strstr(log_buf, "gate by t_gate\n"));
	assert(strstr(log_buf, "target dest NIL\n") || strstr(log_buf, "target dest \n"));
	assert(strstr(log_buf, "other t_gate\n") && strstr(log_buf, "other none\n"));
	assert(strstr(log_buf, "runto: not an actor (trigger_multiple $t_gate)"));
	assert(strstr(log_buf, "setthread no_label: no such label in maps/g.scr"));
	assert(strstr(log_buf, "mohaa: could not load global/nothere.scr (scripts hold "));
	assert(!strstr(log_buf, "lighton") && !strstr(log_buf, "disconnect_paths") && !strstr(log_buf, "holster"));
	assert(strstr(log_buf, "tag (0.000 0.000 0.000)\n"));
	assert(near(ents[t].vel[0], 72.0f));
	assert(!strcmp(cvar_set, "g_mohaa=1"));
	assert(strstr(log_buf, "[center] Objective: Find the radio\n"));
	assert(strstr(log_buf, "ahead (0.000 128.000 0.000)\n") || strstr(log_buf, "ahead (-0.000 128.000 0.000)\n"));
	assert(strstr(log_buf, "set 4 group left side\n"));
	assert(strstr(log_buf, "spawned set 4\n"));
	assert(strstr(log_buf, "turret t_gate\n"));
	assert(strstr(log_buf, "left (-1.000 ") && strstr(log_buf, " up (0.000 0.000 1.000)") );
}

/* main waits for the first frame (the map's entities spawn after the VM, during level load); a placeholder's
   map keys go with the entity that replaces it, also through an id no entity has (a soldier waiting for a slot). */
static void test_late_entities_and_moved_keys(void)
{
	DodMohaaBackend b = backend();
	int holder, grunt;
	reset();
	files[0][0] = "maps/l.scr";
	files[0][1] =
		"main:\n"
		"\tprintln (\"late \" + $late.targetname + \" set \" + $soldier.set + \" type \" + $soldier.friendtype)\n"
		"end\n";
	assert(Dod_MohaaLevelInit(&b, "l", 0, 0));
	assert(!strstr(log_buf, "late "));
	add("late", "info_target", 0, 0, 0);            /* spawns after the world, before the first frame */
	holder = add("", "mohaa_actor", 0, 0, 0);
	Dod_MohaaEntityKey(make_id(holder), "#set", "2");
	Dod_MohaaEntityKey(make_id(holder), "#friendtype", "1");
	Dod_MohaaEntityMoved(make_id(holder), 7u << 12);   /* parked while it waits */
	grunt = add("soldier", "actor", 0, 0, 0);
	Dod_MohaaEntityKey(make_id(grunt), "#friendtype", "4");   /* the new body's own value wins */
	Dod_MohaaEntityMoved(7u << 12, make_id(grunt));
	Dod_MohaaThink(0.05f);
	assert(strstr(log_buf, "late late set 2 type 4\n"));
}

/* Walk the region block by block and the free list: tags agree, no two free blocks touch, the list is in
   address order and holds exactly the free blocks, and the used count matches. */
static void pool_check(const MohaaPool *p)
{
	size_t used = 0, nfree = 0, nlist = 0, total = 0;
	int r;
	const MohaaPoolFree *f, *last = NULL;
	for (r = 0; r < p->nregions; r++) {
		const unsigned char *b = p->rbase[r];
		int prev_free = 0;
		size_t edge;
		memcpy(&edge, b - sizeof(edge), sizeof(edge));
		assert(edge == 1);   /* the busy tags at the region's ends */
		memcpy(&edge, b + p->rsize[r], sizeof(edge));
		assert(edge == 1);
		while (b < p->rbase[r] + p->rsize[r]) {
			size_t head, foot;
			memcpy(&head, b, sizeof(head));
			memcpy(&foot, b + (head & ~(size_t)1) - sizeof(foot), sizeof(foot));
			assert(head == foot && (head & ~(size_t)1) >= MP_MIN);
			if (head & 1u) {
				used += head & ~(size_t)1;
				prev_free = 0;
			} else {
				assert(!prev_free);
				prev_free = 1;
				nfree++;
			}
			b += head & ~(size_t)1;
		}
		assert(b == p->rbase[r] + p->rsize[r]);
		total += p->rsize[r];
	}
	assert(used == p->used && total == p->size);
	for (f = p->free; f; f = f->next) {
		assert(!mp_busy(f) && f->prev == last && (!last || last < f));
		last = f;
		nlist++;
	}
	assert(last == p->tail && nlist == nfree);
}

/* The region allocator: random allocs, grows, shrinks and frees keep every block's bytes, and freeing
   everything merges the region back into one piece. */
static void test_pool_allocator(void)
{
	static unsigned char region[64 * 1024 + 3];
	enum { N = 200 };
	MohaaPool p;
	unsigned char *ptr[N];
	size_t len[N];
	uint32_t rng = 12345u;
	size_t whole;
	int i, k;
	assert(!MohaaPool_Init(&p, region, 8));
	assert(MohaaPool_Init(&p, region + 3, sizeof(region) - 3));   /* unaligned start is trimmed */
	whole = MohaaPool_Largest(&p);
	assert(whole > 63 * 1024);
	memset(ptr, 0, sizeof(ptr));
	for (k = 0; k < 20000; k++) {
		rng = rng * 1103515245u + 12345u;
		i = (int)((rng >> 8) % N);
		if (k % 97 == 0)
			pool_check(&p);
		MohaaPool_Top(&p, (k / 500) % 3 == 1);   /* stretches of top-down (compile) allocation */
		const size_t want = 1 + (rng >> 20) % 900;
		if (ptr[i]) {   /* check the block kept its fill byte */
			size_t j;
			for (j = 0; j < len[i]; j++)
				assert(ptr[i][j] == (unsigned char)i);
		}
		if (ptr[i] && (rng & 3u) == 0) {
			MohaaPool_Free(&p, ptr[i]);
			ptr[i] = NULL;
		} else {
			unsigned char *q = (unsigned char *)MohaaPool_Realloc(&p, ptr[i], want);
			if (!q)
				continue;   /* full: the old block is untouched */
			if (want > (ptr[i] ? len[i] : 0))
				memset(q + (ptr[i] ? len[i] : 0), i, want - (ptr[i] ? len[i] : 0));
			ptr[i] = q;
			len[i] = want;
		}
	}
	pool_check(&p);
	MohaaPool_Top(&p, 0);
	for (i = 0; i < N; i++)
		MohaaPool_Free(&p, ptr[i]);
	pool_check(&p);
	assert(p.used == 0 && MohaaPool_Largest(&p) == whole && p.free && !p.free->next);
	assert(!MohaaPool_Alloc(&p, whole + 1) && MohaaPool_Alloc(&p, whole));

	/* compile pattern: kept buffers interleave with scratch blocks; scratch on top leaves one hole */
	{
		void *keep[16], *tmp[16];
		uintptr_t lowest_tmp = ~(uintptr_t)0, highest_keep = 0;
		assert(MohaaPool_Init(&p, region, sizeof(region)));
		for (i = 0; i < 16; i++) {
			MohaaPool_Top(&p, 1);
			tmp[i] = MohaaPool_Alloc(&p, 2000);
			MohaaPool_Top(&p, 0);
			keep[i] = MohaaPool_Alloc(&p, 300);
			assert(tmp[i] && keep[i]);
			if ((uintptr_t)tmp[i] < lowest_tmp)
				lowest_tmp = (uintptr_t)tmp[i];
			if ((uintptr_t)keep[i] > highest_keep)
				highest_keep = (uintptr_t)keep[i];
		}
		assert(highest_keep < lowest_tmp);
		for (i = 0; i < 16; i++)
			MohaaPool_Free(&p, tmp[i]);
		assert(p.free && !p.free->next);   /* the scratch merged back into the one free block above */
		assert(MohaaPool_Largest(&p) > sizeof(region) - 16 * 400);
		/* top-mode growth by realloc moves within the top */
		MohaaPool_Top(&p, 1);
		tmp[0] = MohaaPool_Realloc(&p, NULL, 100);
		tmp[0] = MohaaPool_Realloc(&p, tmp[0], 5000);
		assert(tmp[0] && (uintptr_t)tmp[0] > highest_keep);
		MohaaPool_Free(&p, tmp[0]);
		MohaaPool_Top(&p, 0);
		for (i = 0; i < 16; i++)
			MohaaPool_Free(&p, keep[i]);
		assert(p.used == 0 && p.free && !p.free->next && p.free == p.tail);
	}

	/* three regions apart (a split arena tail): blocks never merge across a region's edge */
	{
		static unsigned char r2[3][8 * 1024 + 5];
		void *q[64];
		int n = 0;
		assert(MohaaPool_Init(&p, r2[1] + 1, sizeof(r2[1]) - 1));
		assert(MohaaPool_AddRegion(&p, r2[0], sizeof(r2[0])) && MohaaPool_AddRegion(&p, r2[2] + 5, sizeof(r2[2]) - 5));
		assert(p.nregions == 3 && p.free && p.free->next && p.free->next->next && !p.free->next->next->next);
		assert(MohaaPool_Largest(&p) < 8 * 1024 && !MohaaPool_Alloc(&p, 9 * 1024));
		while (n < 64 && (q[n] = MohaaPool_Alloc(&p, 700)) != NULL)
			n++;
		assert(n >= 30);   /* all three regions fill */
		pool_check(&p);
		for (i = 0; i < n; i += 2)
			MohaaPool_Free(&p, q[i]);
		pool_check(&p);
		for (i = 1; i < n; i += 2)
			MohaaPool_Free(&p, q[i]);
		pool_check(&p);
		assert(p.used == 0 && p.free->next && p.free->next->next && !p.free->next->next->next);
	}
}

/* A backend region replaces malloc: the level runs in it, and one too small refuses cleanly. */
static void test_pool_backend(void)
{
	static unsigned char region[96 * 1024];
	DodMohaaBackend b = backend();
	DodMohaaStats st;
	reset();
	add("door1", "func_wall", 0, 0, 0);
	files[0][0] = "maps/p.scr";
	files[0][1] =
		"main:\n"
		"\tlevel waittill spawn\n"
		"\tfor (local.i = 0; local.i < 50; local.i++)\n"
		"\t\tlevel.list[local.i] = \"item \" + local.i\n"
		"\tprintln \"pooled \" level.list[49] \" \" $door1.origin\n"
		"end\n";
	b.pool = region;
	b.pool_size = sizeof(region) / 2;   /* in two pieces, as a split arena tail gives it */
	b.pool_more[0] = region + sizeof(region) / 2 + 64;
	b.pool_more_size[0] = sizeof(region) / 2 - 64;
	assert(Dod_MohaaLevelInit(&b, "p", 0, 0));
	run(0.05f, 0.3f);
	assert(strstr(log_buf, "pooled item 49 (0.000 0.000 0.000)"));
	Dod_MohaaGetStats(&st);
	assert(st.errors == 0 && st.memory > 0);
	Dod_MohaaShutdown();
	reset();
	files[0][0] = "maps/p.scr";
	files[0][1] = "main:\n\tprintln \"x\"\nend\n";
	b.pool_size = sizeof(region);
	b.pool_more[0] = NULL;
	b.pool_more_size[0] = 0;
	assert(Dod_MohaaLevelInit(&b, "p", 0, 0));
	/* the region is taken back (GameCube map arena reset): the script stops and nothing touches it again */
	memset(region, 0xA5, sizeof(region));
	Dod_MohaaDropPool();
	Dod_MohaaGetStats(&st);
	assert(!st.active);
	Dod_MohaaThink(1.0f);
	Dod_MohaaShutdown();
	Dod_MohaaDropPool();   /* no pool in use: nothing to do */
	/* a pool too small for the level: the rest goes to the heap, and dropping the pool frees that too (ASan) */
	reset();
	files[0][0] = "maps/p.scr";
	files[0][1] =
		"main:\n"
		"\tfor (local.i = 0; local.i < 200; local.i++)\n"
		"\t\tlevel.list[local.i] = \"item \" + local.i\n"
		"\tprintln \"overflow \" level.list[199]\n"
		"\twait 5\n"
		"end\n";
	b.pool_size = 8 * 1024;
	assert(Dod_MohaaLevelInit(&b, "p", 0, 0));
	run(0.05f, 0.3f);
	assert(strstr(log_buf, "overflow item 199"));
	Dod_MohaaGetStats(&st);
	assert(st.errors == 0 && st.memory > b.pool_size);
	Dod_MohaaDropPool();
	/* and with a budget, running out still says where the memory went */
	reset();
	files[0][0] = "maps/p.scr";
	files[0][1] =
		"main:\n"
		"\tfor (local.i = 0; local.i < 5000; local.i++)\n"
		"\t\tlevel.list[local.i] = \"item \" + local.i\n"
		"end\n";
	b.pool_size = 8 * 1024;
	assert(Dod_MohaaLevelInit(&b, "p", 0, 48 * 1024));
	run(0.05f, 0.3f);
	assert(strstr(log_buf, "out of memory") && strstr(log_buf, "more on the engine heap"));
	Dod_MohaaShutdown();
}

static void test_vehicle_drive(void)
{
	DodMohaaBackend b = backend();
	int truck, p1, p2, p3;
	reset();
	truck = add("truck", "info_target", 0, 0, 0);
	p1 = add("p1", "info_target", 100, 0, 0);
	p2 = add("p2", "info_target", 100, 100, 0);
	p3 = add("p3", "info_target", 0, 100, 0);
	strcpy(ents[p1].target, "p2");
	strcpy(ents[p2].target, "p3");
	files[0][0] = "maps/v.scr";
	files[0][1] =
		"main:\n"
		"\tlevel waittill spawn\n"
		"\t$truck lock\n"
		"\t$truck attachdriverslot 0 $truck\n"
		"\t$truck drive $p1 400 100 200 256\n"
		"\t$truck waittill drive\n"
		"\tprintln (\"arrived \" + level.time)\n"
		"\t$truck drive $p1 400\n"
		"\t$truck stop\n"
		"\tprintln \"stopped\"\n"
		"\t$truck followpath $p1 \"loop\"\n"
		"\twait 2\n"
		"\t$truck endpath\n"
		"\t$truck angles (0 10 0)\n"
		"\t$truck time 0\n"
		"\t$truck rotateyup 30\n"
		"\t$truck rotatexdown 5\n"
		"\t$truck waitmove\n"
		"\t$truck health 100\n"
		"\t$truck damage $truck 40 $truck (0 0 0) (0 0 0) (0 0 0) 0 0 0\n"
		"\t$truck say dfr_nothere\n"
		"\t$truck physics_velocity (0 0 0)\n"
		"\tprintln (\"turned \" + $truck.angles + \" health \" + $truck.health)\n"
		"end\n";
	assert(Dod_MohaaLevelInit(&b, "v", 0, 0));
	run(0.05f, 6.0f);
	assert(strstr(log_buf, "arrived ") && strstr(log_buf, "stopped"));
	assert(strstr(log_buf, "turned (-5.000 40.000 0.000) health 60.000"));
	(void)p2; (void)p3; (void)truck;
	Dod_MohaaShutdown();
}

int main(void)
{
	test_no_script_no_vm();
	test_level_flow_and_movers();
	test_waittill_trigger_and_freed();
	test_budget_refuses_cleanly();
	test_actors();
	test_sounds();
	test_music();
	test_routes();
	test_setthread_and_quiet_commands();
	test_late_entities_and_moved_keys();
	test_pool_allocator();
	test_pool_backend();
	test_vehicle_drive();
	Dod_MohaaShutdown();
	assert(Dod_MohaaPathNodes(NULL) == 0);
	printf("dod_mohaa_test: ok\n");
	return 0;
}
