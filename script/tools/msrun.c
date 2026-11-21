/*
 * msrun - run a MOHAA .scr against a mock world, for tests and for checking
 * real mission scripts on a PC before they reach the GameCube. MIT licensed.
 *
 *   msrun [-root DIR] [-time SECONDS] [-label NAME] [-mem] [-stats] [-budget BYTES] file.scr
 *   msrun -compile file.scr...     compile only; one line per failure, then a summary
 *
 * The world is described by comment directives in the script itself:
 *   //@ent <targetname> <classname> [x y z]   create an entity
 *   //@at <time> notify <targetname|level> <event>
 *   //@at <time> remove <targetname>
 *   //@run <seconds>                           how long to simulate (default 10)
 *
 * Every entity command nobody else handles is logged as
 *   "<time> $<targetname> <command> <args...>"
 * so tests can check what a script asked the world to do.
 */
#include "morpheus.h"
#include "../src/ms_internal.h"   /* -stats reads the VM's tables */

#include <stdarg.h>
#include <stddef.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ENTS 256
#define MAX_EVENTS 128

typedef struct ent {
    int alive;
    char targetname[64];
    char classname[64];
    float origin[3];
    float health;
} ent;

typedef struct event {
    float time;
    int kind;   /* 0 notify, 1 remove */
    char target[64];
    char name[64];
    int done;
} event;

static ent ents[MAX_ENTS];
static int nents;
static event events[MAX_EVENTS];
static int nevents;
static char root[512] = ".";
static ms_vm *vm;

static void out(const char *fmt, ...)
{
    va_list ap;
    printf("%6.2f ", vm ? (double)ms_time(vm) : 0.0);
    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
}

static int add_ent(const char *tn, const char *cls, float x, float y, float z)
{
    if (nents == MAX_ENTS)
        return -1;
    ent *e = &ents[nents];
    memset(e, 0, sizeof(*e));
    e->alive = 1;
    snprintf(e->targetname, sizeof(e->targetname), "%s", tn);
    snprintf(e->classname, sizeof(e->classname), "%s", cls);
    e->origin[0] = x;
    e->origin[1] = y;
    e->origin[2] = z;
    e->health = 100;
    return nents++;
}

/* entity ids are index + 1 so 0 is never valid */
static ent *get_ent(uint32_t id)
{
    if (id < 1 || id > (uint32_t)nents || !ents[id - 1].alive)
        return NULL;
    return &ents[id - 1];
}

static const char *ent_name(const ms_value *v)
{
    static char buf[80];
    if (v->type == MS_ENTITY) {
        ent *e = get_ent(v->u.id);
        snprintf(buf, sizeof(buf), "$%s", e ? (e->targetname[0] ? e->targetname : e->classname) : "?");
    } else
        snprintf(buf, sizeof(buf), "%s", ms_type_name(v->type));
    return buf;
}

/* ---- host callbacks ---- */

static char *load_file(void *user, const char *path, size_t *len)
{
    (void)user;
    char full[1024];
    snprintf(full, sizeof(full), "%s/%s", root, path);
    FILE *f = fopen(full, "rb");
    if (!f)
        return NULL;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = (char *)malloc((size_t)n + 1);
    if (!buf) {
        fclose(f);
        return NULL;
    }
    *len = fread(buf, 1, (size_t)n, f);
    buf[*len] = 0;
    fclose(f);
    return buf;
}

static void print(void *user, int channel, const char *text)
{
    (void)user;
    static const char *prefix[] = {"", "[debug] ", "[hud] ", "[hud bold] ", "[error] "};
    out("%s%s", prefix[channel], text);
}

static int find_targetname(void *user, const char *name, uint32_t *ids, int max)
{
    (void)user;
    int n = 0;
    for (int i = 0; i < nents; i++) {
        if (ents[i].alive && strcmp(ents[i].targetname, name) == 0) {
            if (n < max)
                ids[n] = (uint32_t)i + 1;
            n++;
        }
    }
    return n;
}

static int entity_valid(void *user, uint32_t id)
{
    (void)user;
    return get_ent(id) != NULL;
}

static int get_field(void *user, const ms_value *l, const char *name, ms_value *o)
{
    (void)user;
    if (l->type != MS_ENTITY)
        return 0;
    ent *e = get_ent(l->u.id);
    if (!e)
        return 0;
    if (!strcmp(name, "origin")) {
        *o = ms_vec(e->origin[0], e->origin[1], e->origin[2]);
        return 1;
    }
    if (!strcmp(name, "health")) {
        *o = ms_float(e->health);
        return 1;
    }
    if (!strcmp(name, "targetname")) {
        *o = ms_string(vm, e->targetname);
        return 1;
    }
    if (!strcmp(name, "classname")) {
        *o = ms_string(vm, e->classname);
        return 1;
    }
    return 0;
}

static int set_field(void *user, const ms_value *l, const char *name, const ms_value *v)
{
    (void)user;
    if (l->type != MS_ENTITY)
        return 0;
    ent *e = get_ent(l->u.id);
    if (!e)
        return 0;
    if (!strcmp(name, "origin") && v->type == MS_VECTOR) {
        memcpy(e->origin, v->u.v, sizeof(e->origin));
        return 1;
    }
    if (!strcmp(name, "health")) {
        e->health = ms_to_float(v);
        return 1;
    }
    if (!strcmp(name, "targetname")) {
        char buf[64];
        snprintf(e->targetname, sizeof(e->targetname), "%s", ms_tostring(v, buf, sizeof(buf)));
        return 1;
    }
    return 0;
}

static void log_call(ms_call *c)
{
    char line[512];
    size_t o = 0;
    o += (size_t)snprintf(line + o, sizeof(line) - o, "%s %s", ent_name(ms_call_target(c)), ms_call_name(c));
    for (int i = 0; i < ms_argc(c) && o < sizeof(line); i++) {
        const ms_value *a = ms_arg(c, i);
        if (a->type == MS_ENTITY)
            o += (size_t)snprintf(line + o, sizeof(line) - o, " %s", ent_name(a));
        else
            o += (size_t)snprintf(line + o, sizeof(line) - o, " %s", ms_arg_string(c, i));
    }
    out("%s\n", line);
}

static int unknown_command(ms_call *c)
{
    if (ms_call_target(c)->type != MS_ENTITY)
        return 0;
    log_call(c);
    return 1;
}

static float rnd_state = 0.0f;
static float rnd(void *user)
{
    (void)user;
    rnd_state += 0.618034f;
    if (rnd_state >= 1.0f)
        rnd_state -= 1.0f;
    return rnd_state;
}

/* ---- mock game commands ---- */

static int c_spawn(ms_call *c)
{
    const char *cls = ms_arg_string(c, 0);
    int i = add_ent("", cls, 0, 0, 0);
    if (i < 0)
        return ms_call_error(c, "too many entities");
    for (int k = 1; k + 1 < ms_argc(c); k += 2) {
        if (!strcmp(ms_arg_string(c, k), "targetname"))
            snprintf(ents[i].targetname, sizeof(ents[i].targetname), "%s", ms_arg_string(c, k + 1));
        else if (!strcmp(ms_arg_string(c, k), "origin"))
            ms_arg_vector(c, k + 1, ents[i].origin);
    }
    out("spawn %s%s%s\n", cls, ents[i].targetname[0] ? " $" : "", ents[i].targetname);
    ms_return_entity(c, (uint32_t)i + 1);
    return 0;
}

static int c_remove(ms_call *c)
{
    const ms_value *t = ms_call_target(c);
    ent *e = get_ent(t->u.id);
    if (!e)
        return 0;
    log_call(c);
    e->alive = 0;
    ms_entity_removed(ms_call_vm(c), t->u.id);
    return 0;
}

static int c_trigger(ms_call *c)
{
    const ms_value *t = ms_arg(c, 0);
    out("trigger %s\n", ent_name(t));
    if (t->type == MS_ENTITY)
        ms_notify(ms_call_vm(c), t, "trigger");
    return 0;
}

static int c_waitmove(ms_call *c)
{
    log_call(c);
    ms_call_wait_time(c, 1.0f);   /* mock movers take one second */
    return 0;
}

static int c_moveto(ms_call *c)
{
    log_call(c);
    return 0;
}

static int c_getcvar(ms_call *c)
{
    ms_return_string(c, "");
    return 0;
}

/* ---- directives ---- */

static float parse_directives(const char *text)
{
    float run = 10.0f;
    const char *p = text;
    while ((p = strstr(p, "//@")) != NULL) {
        p += 3;
        char line[256];
        size_t n = strcspn(p, "\r\n");
        if (n >= sizeof(line))
            n = sizeof(line) - 1;
        memcpy(line, p, n);
        line[n] = 0;
        char a[64], b[64], d[64], e2[64];
        float x = 0, y = 0, z = 0, tm;
        if (sscanf(line, "ent %63s %63s %f %f %f", a, b, &x, &y, &z) >= 2) {
            add_ent(a, b, x, y, z);
        } else if (sscanf(line, "at %f %63s %63s %63s", &tm, d, a, e2) >= 3 && nevents < MAX_EVENTS) {
            event *ev = &events[nevents++];
            memset(ev, 0, sizeof(*ev));
            ev->time = tm;
            ev->kind = strcmp(d, "remove") == 0;
            snprintf(ev->target, sizeof(ev->target), "%s", a);
            if (!ev->kind)
                snprintf(ev->name, sizeof(ev->name), "%s", e2);
        } else if (sscanf(line, "run %f", &tm) == 1) {
            run = tm;
        }
    }
    return run;
}

static void fire_event(event *ev)
{
    ms_value l = ms_nil();
    if (!strcmp(ev->target, "level")) {
        l.type = MS_LEVEL;
        out("<notify level %s>\n", ev->name);
        ms_notify(vm, &l, ev->name);
        return;
    }
    for (int i = 0; i < nents; i++) {
        if (!ents[i].alive || strcmp(ents[i].targetname, ev->target) != 0)
            continue;
        if (ev->kind) {
            out("<remove $%s>\n", ev->target);
            ents[i].alive = 0;
            ms_entity_removed(vm, (uint32_t)i + 1);
        } else {
            out("<notify $%s %s>\n", ev->target, ev->name);
            l = ms_entity((uint32_t)i + 1);
            ms_notify(vm, &l, ev->name);
        }
    }
}

static int compile_only(int argc, char **argv, int first)
{
    ms_host host;
    memset(&host, 0, sizeof(host));
    host.print = print;
    vm = ms_create(&host, NULL);
    if (!vm)
        return 2;
    int ok = 0, bad = 0;
    size_t peak = 0;
    for (int i = first; i < argc; i++) {
        snprintf(root, sizeof(root), ".");
        size_t len = 0;
        char *text = load_file(NULL, argv[i], &len);
        if (!text) {
            printf("missing %s\n", argv[i]);
            bad++;
            continue;
        }
        size_t before = ms_memory_used(vm);
        if (ms_load_text(vm, argv[i], text, len)) {
            ok++;
            if (ms_memory_used(vm) - before > peak)
                peak = ms_memory_used(vm) - before;
        } else
            bad++;
        free(text);
    }
    printf("compiled %d of %d scripts, %zu bytes of bytecode and tables in total, largest %zu\n", ok, ok + bad,
           ms_memory_used(vm), peak);
    ms_destroy(vm);
    return bad ? 1 : 0;
}

/* -stats: where the VM's memory goes, by kind (allocation headers included). */
#define AH 8
static void print_stats(const ms_vm *v)
{
    size_t code = 0, consts = 0, cstr = 0, labels = 0, sw = 0, lines = 0, paths = 0;
    int nscripts = 0;
    printf("%-36s %8s %7s %6s %6s %6s\n", "script", "code", "consts", "labels", "lines", "total");
    for (const ms_script *s = v->scripts; s; s = s->next) {
        size_t cs = 0;
        for (uint32_t i = 0; i < s->nconsts; i++)
            cs += (offsetof(ms_str, data) + s->consts[i]->len + 1 + 7) & ~(size_t)7;
        if (s->pool)
            cs += AH + ((sizeof(ms_pool) + 7) & ~(size_t)7);
        size_t swb = s->nswitches ? s->nswitches * sizeof(ms_switch) + AH : 0;
        for (uint32_t i = 0; i < s->nswitches; i++)
            swb += s->switches[i].n * sizeof(ms_case) + AH;
        size_t c = s->code_len + AH, k = s->nconsts * sizeof(ms_str *) + AH + cs;
        size_t l = s->nlabels * sizeof(ms_label) + AH, ln = s->lines_len + AH;
        size_t total = c + k + l + ln + swb + strlen(s->path) + 1 + AH + sizeof(ms_script) + AH;
        printf("%-36s %8zu %7zu %6zu %6zu %6zu\n", s->path, c, k, l, ln, total);
        code += c; consts += s->nconsts * sizeof(ms_str *) + AH; cstr += cs; labels += l; sw += swb; lines += ln;
        paths += strlen(s->path) + 1 + AH + sizeof(ms_script) + AH;
        nscripts++;
    }
    size_t names = v->names.cap * (sizeof(char *) + sizeof(uint32_t)) + v->names.icap * sizeof(uint32_t) + 3 * AH;
    for (uint32_t i = 0; i < v->names.n; i++)
        names += strlen(v->names.str[i]) + 1 + AH;
    size_t cmds = v->ncmds * sizeof(ms_cmd *) + AH;
    for (uint32_t i = 0; i < v->ncmds; i++)
        for (const ms_cmd *c = v->cmds[i]; c; c = c->next)
            cmds += sizeof(ms_cmd) + AH;
    size_t threads = 0;
    int nthreads = 0;
    for (const ms_thread *t = v->threads; t; t = t->next) {
        threads += sizeof(ms_thread) + AH + (size_t)t->scap * sizeof(ms_value) + AH +
                   t->locals.cap * (sizeof(uint32_t) + sizeof(ms_value)) + (t->locals.cap ? 2 * AH : 0);
        nthreads++;
    }
    printf("--\n%d scripts: code %zu, const table %zu, const strings %zu, labels %zu, switches %zu, lines %zu, "
           "headers %zu\n", nscripts, code, consts, cstr, labels, sw, lines, paths);
    printf("names %u (%zu bytes), commands %zu, %d threads %zu\n", v->names.n, names, cmds, nthreads, threads);
    printf("in use %zu, peak %zu\n", v->mem_used, v->mem_peak);
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "-compile"))
        return compile_only(argc, argv, 2);
    const char *file = NULL, *label = NULL;
    float run_override = -1.0f;
    int show_mem = 0;
    ms_config cfg;
    memset(&cfg, 0, sizeof(cfg));
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-root") && i + 1 < argc)
            snprintf(root, sizeof(root), "%s", argv[++i]);
        else if (!strcmp(argv[i], "-time") && i + 1 < argc)
            run_override = (float)atof(argv[++i]);
        else if (!strcmp(argv[i], "-label") && i + 1 < argc)
            label = argv[++i];
        else if (!strcmp(argv[i], "-mem"))
            show_mem = 1;
        else if (!strcmp(argv[i], "-stats"))
            show_mem = 2;
        else if (!strcmp(argv[i], "-budget") && i + 1 < argc)
            cfg.memory_budget = (size_t)atol(argv[++i]);
        else
            file = argv[i];
    }
    if (!file) {
        fprintf(stderr, "usage: msrun [-root DIR] [-time S] [-label NAME] [-mem] [-budget BYTES] file.scr\n");
        return 2;
    }
    /* file path relative to root, as the game would name it */
    const char *rel = file;
    size_t rl = strlen(root);
    if (strncmp(file, root, rl) == 0 && file[rl] == '/')
        rel = file + rl + 1;
    else if (!strcmp(root, ".")) {
        const char *slash = strrchr(file, '/');
        if (slash) {
            snprintf(root, sizeof(root), "%.*s", (int)(slash - file), file);
            rel = slash + 1;
        }
    }

    size_t len = 0;
    char *text = load_file(NULL, rel, &len);
    if (!text) {
        fprintf(stderr, "msrun: cannot read %s/%s\n", root, rel);
        return 2;
    }
    float run = parse_directives(text);
    free(text);
    if (run_override >= 0.0f)
        run = run_override;

    ms_host host;
    memset(&host, 0, sizeof(host));
    host.load_file = load_file;
    host.print = print;
    host.find_targetname = find_targetname;
    host.entity_valid = entity_valid;
    host.get_field = get_field;
    host.set_field = set_field;
    host.unknown_command = unknown_command;
    host.random = rnd;
    vm = ms_create(&host, &cfg);
    if (!vm) {
        fprintf(stderr, "msrun: cannot create vm\n");
        return 2;
    }
    ms_register(vm, "spawn", MS_ON_THREAD, c_spawn, NULL);
    ms_register(vm, "trigger", MS_ON_THREAD, c_trigger, NULL);
    ms_register(vm, "getcvar", MS_ON_THREAD, c_getcvar, NULL);
    ms_register(vm, "remove", MS_ON_ENTITY, c_remove, NULL);
    ms_register(vm, "delete", MS_ON_ENTITY, c_remove, NULL);
    ms_register(vm, "waitmove", MS_ON_ENTITY, c_waitmove, NULL);
    ms_register(vm, "moveto", MS_ON_ENTITY, c_moveto, NULL);

    int rc = 0;
    if (!ms_exec(vm, rel, label, NULL, NULL, 0))
        rc = 1;
    const float dt = 0.05f;
    int steps = (int)(run / dt + 0.5f);
    for (int s = 1; s <= steps && rc == 0; s++) {
        float now = (float)s * dt;
        ms_frame(vm, now);
        for (int i = 0; i < nevents; i++) {
            if (!events[i].done && events[i].time <= now + 0.0001f) {
                events[i].done = 1;
                fire_event(&events[i]);
            }
        }
        int pending = 0;
        for (int i = 0; i < nevents; i++)
            pending |= !events[i].done;
        if (!ms_thread_count(vm) && !pending)
            break;
    }
    if (show_mem == 2)
        print_stats(vm);
    else if (show_mem)
        printf("memory: %zu bytes in use, %zu peak, %d threads, %d errors\n", ms_memory_used(vm),
               ms_memory_peak(vm), ms_thread_count(vm), ms_error_count(vm));
    if (ms_error_count(vm) && rc == 0)
        rc = 3;
    ms_destroy(vm);
    return rc;
}
