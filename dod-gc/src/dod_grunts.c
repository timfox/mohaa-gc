/* Grunt rules; see dod_grunts.h. */
#include "dod_grunts.h"

#include <math.h>
#include <string.h>

static float wrap180(float a)
{
	while (a >= 180.0f)
		a -= 360.0f;
	while (a < -180.0f)
		a += 360.0f;
	return a;
}

static int in_leash(const DodGruntPool *p, int i, float nx, float ny);

int DodGrunt_RowBytes(void)
{
	const DodGruntPool *p = 0;
	return (int)(sizeof(DodGruntPool) - sizeof(p->cap) - sizeof(p->rng) - sizeof(p->look_cursor) - sizeof(p->stats)) / DOD_GRUNT_MAX;
}

int Dod_GruntTargetCount(int requested, int edicts_free)
{
	int room = edicts_free - DOD_GRUNT_EDICT_RESERVE;
	int n = requested;
	if (n > DOD_GRUNT_MAX)
		n = DOD_GRUNT_MAX;
	if (n > room)
		n = room;
	return n < 0 ? 0 : n;
}

void DodGrunt_Init(DodGruntPool *p, unsigned seed)
{
	memset(p, 0, sizeof(*p));
	p->rng = seed ? seed : 0x9E3779B9u;
}

float DodGrunt_Rand(DodGruntPool *p)
{
	unsigned x = p->rng;
	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	p->rng = x;
	return (float)(x >> 8) / 16777216.0f;
}

float DodGrunt_YawTo(float x, float y, float tx, float ty)
{
	return atan2f(ty - y, tx - x) * 57.29578f;
}

void DodGrunt_Spawn(DodGruntPool *p, int i, int team, float x, float y, float z, float yaw, float now, int rush)
{
	p->x[i] = x;
	p->y[i] = y;
	p->z[i] = z;
	p->yaw[i] = yaw;
	p->heading[i] = yaw;
	p->phase[i] = DodGrunt_Rand(p) * 256.0f;
	/* A fresh look after a random delay, so a wave of spawns does not look on the same frame. */
	p->next_look[i] = now + DodGrunt_Rand(p) * DOD_GRUNT_SENSE_INTERVAL;
	p->next_check[i] = now + DodGrunt_Rand(p) * DOD_GRUNT_MOVE_CHECK;
	p->next_fire[i] = now + 0.5f + DodGrunt_Rand(p);
	p->turn_at[i] = now + 2.0f + DodGrunt_Rand(p) * 3.0f;
	p->respawn_at[i] = 0.0f;
	p->target_seen[i] = -1000.0f;
	p->hp[i] = DOD_GRUNT_HEALTH;
	p->target[i] = 0;
	p->team[i] = (unsigned char)team;
	p->blocked[i] = 0;
	p->script[i] = 0;
	p->order[i] = DOD_GRUNT_ORDER_NONE;
	p->order_done[i] = 0;
	p->sight[i] = p->hearing[i] = p->leash_r[i] = p->mindist[i] = p->maxdist[i] = 0;
	p->leash_x[i] = p->leash_y[i] = 0;
	p->fov[i] = 0;
	p->cover[i] = DOD_GRUNT_COVER_NONE;
	p->gun[i] = 0;
	p->accuracy[i] = 0;
	p->state[i] = rush ? DOD_GRUNT_ADVANCE : DOD_GRUNT_WANDER;
	if (i >= p->cap)
		p->cap = i + 1;
}

static int alive(const DodGruntPool *p, int i)
{
	return p->state[i] >= DOD_GRUNT_WANDER;
}

int DodGrunt_DueLooks(DodGruntPool *p, float now, int budget, int *out)
{
	int n = 0, k;
	for (k = 0; k < p->cap; k++) {
		const int i = (p->look_cursor + k) % p->cap;
		if (!alive(p, i) || p->next_look[i] > now)
			continue;
		if (n >= budget) {
			p->stats.deferred++;
			continue;
		}
		out[n++] = i;
	}
	if (n > 0)
		p->look_cursor = (out[n - 1] + 1) % p->cap;
	return n;
}

void DodGrunt_Looked(DodGruntPool *p, int i, float now, int visible, int target, float tx, float ty, float dist, int rush)
{
	p->stats.looks++;
	/* +-25% jitter keeps the looks spread out over time. */
	p->next_look[i] = now + DOD_GRUNT_SENSE_INTERVAL * (0.75f + 0.5f * DodGrunt_Rand(p));
	if (p->script[i]) {
		/* A script actor: off means blind, a move order wins over fighting, and it holds instead of wandering. */
		const int attack = (p->script[i] & DOD_GRUNT_ATTACK) != 0;
		if (visible && (p->script[i] & DOD_GRUNT_SOFT_ORDER) && p->order[i] != DOD_GRUNT_ORDER_NONE
			&& !(p->script[i] & DOD_GRUNT_AI_OFF)) {
			/* a patrol walk ends when an enemy comes into sight */
			p->order[i] = DOD_GRUNT_ORDER_NONE;
			p->script[i] &= (unsigned char)~DOD_GRUNT_SOFT_ORDER;
		}
		if ((p->script[i] & DOD_GRUNT_AI_OFF) || p->order[i] != DOD_GRUNT_ORDER_NONE) {
			p->target[i] = 0;
			return;
		}
		if (visible) {
			p->target[i] = (signed char)target;
			p->target_x[i] = tx;
			p->target_y[i] = ty;
			p->target_seen[i] = now;
			if (p->script[i] & DOD_GRUNT_TURRET) {
				p->state[i] = DOD_GRUNT_SHOOT;	/* the gun reaches anything in its arc; it never leaves it */
				return;
			}
			{
				/* MOHAA maxdist: the range it fights from; mindist: nearer than this it backs off first */
				const float fight = p->maxdist[i] ? (float)p->maxdist[i] : DOD_GRUNT_CLOSE * 3.0f;
				if (attack && p->mindist[i] && dist < (float)p->mindist[i])
					p->state[i] = DOD_GRUNT_ADVANCE;	/* the advance step backs it off */
				else
					p->state[i] = (dist <= fight) ? DOD_GRUNT_SHOOT : (attack ? DOD_GRUNT_ADVANCE : DOD_GRUNT_HOLD);
			}
			if (p->state[i] == DOD_GRUNT_HOLD)
				p->heading[i] = DodGrunt_YawTo(p->x[i], p->y[i], tx, ty);
			return;
		}
		p->target[i] = 0;
		if (p->state[i] == DOD_GRUNT_SHOOT)
			p->state[i] = attack ? DOD_GRUNT_ADVANCE : DOD_GRUNT_HOLD;
		return;
	}
	if (visible) {
		p->target[i] = (signed char)target;
		p->target_x[i] = tx;
		p->target_y[i] = ty;
		p->target_seen[i] = now;
		p->state[i] = (dist <= DOD_GRUNT_CLOSE * 3.0f) ? DOD_GRUNT_SHOOT : (rush ? DOD_GRUNT_ADVANCE : DOD_GRUNT_WANDER);
		return;
	}
	p->target[i] = 0;
	if (p->state[i] == DOD_GRUNT_SHOOT)
		p->state[i] = rush ? DOD_GRUNT_ADVANCE : DOD_GRUNT_WANDER;
}

void DodGrunt_Move(DodGruntPool *p, int i, float now, float dt)
{
	float speed = 0.0f, want_yaw = p->yaw[i], d;
	const int remembers = now - p->target_seen[i] < DOD_GRUNT_MEMORY;
	if (!alive(p, i))
		return;
	if (p->order[i] != DOD_GRUNT_ORDER_NONE) {
		const float dx = p->order_x[i] - p->x[i], dy = p->order_y[i] - p->y[i];
		const float dist = sqrtf(dx * dx + dy * dy);
		/* A scripted walk the world blocks (a truck parked across the line, a wall between it and a tag point)
		 * would never arrive, and a mission waiting on movedone would hang: m1l1's checkpoint guard walked into the
		 * Opel for good. MOHAA's actors path around such things; this one gives up after DOD_GRUNT_ORDER_STALL
		 * seconds without getting nearer and takes its place at the point. */
		if (p->order_stall_at[i] < 0.0f || dist < p->order_best[i] - 8.0f) {
			p->order_best[i] = dist;
			p->order_stall_at[i] = now + DOD_GRUNT_ORDER_STALL;
		} else if (now >= p->order_stall_at[i]) {
			p->x[i] = p->order_x[i];
			p->y[i] = p->order_y[i];
		}
		if (dist <= DOD_GRUNT_ARRIVE || now >= p->order_stall_at[i]) {
			p->order[i] = DOD_GRUNT_ORDER_NONE;
			p->order_done[i] = 1;
			p->state[i] = DOD_GRUNT_HOLD;
		} else {
			/* a blocked check turned the heading away; the next unblocked frame aims at the point again */
			if (!p->blocked[i])
				p->heading[i] = DodGrunt_YawTo(p->x[i], p->y[i], p->order_x[i], p->order_y[i]);
			speed = p->order[i] == DOD_GRUNT_ORDER_RUN ? DOD_GRUNT_RUN : DOD_GRUNT_WALK;
			p->state[i] = p->order[i] == DOD_GRUNT_ORDER_RUN ? DOD_GRUNT_ADVANCE : DOD_GRUNT_WANDER;
			/* never step past the point in one frame */
			if (speed * dt > sqrtf(dx * dx + dy * dy))
				speed = sqrtf(dx * dx + dy * dy) / (dt > 0.0f ? dt : 1.0f);
		}
		want_yaw = p->heading[i];
		goto turn_and_step;
	}
	switch (p->state[i]) {
	case DOD_GRUNT_HOLD:
		want_yaw = p->heading[i];
		break;
	case DOD_GRUNT_SHOOT:
		if (remembers)
			want_yaw = DodGrunt_YawTo(p->x[i], p->y[i], p->target_x[i], p->target_y[i]);
		break;
	case DOD_GRUNT_ADVANCE:
		if (remembers) {
			const float dx = p->target_x[i] - p->x[i], dy = p->target_y[i] - p->y[i];
			const float d2 = dx * dx + dy * dy;
			const float close = p->maxdist[i] ? (float)p->maxdist[i] : DOD_GRUNT_CLOSE;
			if (p->mindist[i] && d2 < (float)p->mindist[i] * (float)p->mindist[i]) {
				/* too near (MOHAA mindist): back off, still facing the enemy */
				p->heading[i] = wrap180(DodGrunt_YawTo(p->x[i], p->y[i], p->target_x[i], p->target_y[i]) + 180.0f);
				speed = DOD_GRUNT_WALK;
				want_yaw = wrap180(p->heading[i] + 180.0f);
				goto turn_and_step;
			}
			if (d2 > close * close) {
				p->heading[i] = DodGrunt_YawTo(p->x[i], p->y[i], p->target_x[i], p->target_y[i]);
				speed = DOD_GRUNT_RUN;
			}
		} else
			speed = DOD_GRUNT_RUN;
		want_yaw = p->heading[i];
		break;
	default:
		if (now >= p->turn_at[i]) {
			p->heading[i] = wrap180(p->heading[i] + (DodGrunt_Rand(p) - 0.5f) * 140.0f);
			p->turn_at[i] = now + 2.0f + DodGrunt_Rand(p) * 4.0f;
		}
		/* Stand still part of the time: a grunt that never stops looks like a conveyor belt. */
		speed = DOD_GRUNT_WALK;
		want_yaw = p->heading[i];
		break;
	}
turn_and_step:
	if (p->blocked[i])
		speed = 0.0f;
	/* The body turns at up to 360 degrees per second. */
	d = wrap180(want_yaw - p->yaw[i]);
	{
		const float step = 360.0f * dt;
		p->yaw[i] = wrap180(p->yaw[i] + (d > step ? step : (d < -step ? -step : d)));
	}
	if (speed > 0.0f) {
		const float r = p->heading[i] * 0.017453293f;
		/* a leashed actor stops at the edge of its leash (a script order may still take it out) */
		if (p->order[i] == DOD_GRUNT_ORDER_NONE
			&& !in_leash(p, i, p->x[i] + cosf(r) * speed * dt, p->y[i] + sinf(r) * speed * dt)
			&& in_leash(p, i, p->x[i], p->y[i]))
			speed = 0.0f;
	}
	if (speed > 0.0f) {
		const float r = p->heading[i] * 0.017453293f;
		p->x[i] += cosf(r) * speed * dt;
		p->y[i] += sinf(r) * speed * dt;
		/* Walk cycle: about one stride per 40 units run, 28 walk, as a fraction of 256 frames. */
		p->phase[i] += speed * dt * (speed > 100.0f ? 3.2f : 4.6f);
		while (p->phase[i] >= 256.0f)
			p->phase[i] -= 256.0f;
	} else {
		p->phase[i] += dt * 14.0f;
		while (p->phase[i] >= 256.0f)
			p->phase[i] -= 256.0f;
	}
}

int DodGrunt_CheckDue(DodGruntPool *p, int i, float now)
{
	if (!alive(p, i) || p->next_check[i] > now)
		return 0;
	p->next_check[i] = now + DOD_GRUNT_MOVE_CHECK;
	/* Only a grunt that is trying to walk needs the probe. */
	return p->state[i] == DOD_GRUNT_WANDER || p->state[i] == DOD_GRUNT_ADVANCE;
}

float DodGrunt_ProbeDistance(const DodGruntPool *p, int i)
{
	return (p->state[i] == DOD_GRUNT_ADVANCE ? DOD_GRUNT_RUN : DOD_GRUNT_WALK) * DOD_GRUNT_MOVE_CHECK * 2.0f + 24.0f;
}

void DodGrunt_MoveChecked(DodGruntPool *p, int i, int clear)
{
	p->stats.move_traces++;
	if (clear) {
		p->blocked[i] = 0;
		return;
	}
	/* Stopped: turn away so the next check finds a way. Reads as the grunt backing off a wall. A turret gunner keeps
	 * its gun's heading: it does not walk. */
	if (!(p->script[i] & DOD_GRUNT_TURRET)) {
		const float turn = 60.0f + DodGrunt_Rand(p) * 120.0f;
		p->heading[i] = wrap180(p->heading[i] + (DodGrunt_Rand(p) < 0.5f ? -turn : turn));
	}
	p->blocked[i] = 1;
	/* Clear the stop at the next check, which probes the new heading. */
}

int DodGrunt_ShotDue(DodGruntPool *p, int i, float now, int skill)
{
	float gap;
	if (p->state[i] != DOD_GRUNT_SHOOT || p->target[i] == 0 || p->next_fire[i] > now)
		return 0;
	if (skill < 0)
		skill = 0;
	if (skill > 3)
		skill = 3;
	gap = (1.0f + DodGrunt_Rand(p)) * (1.0f - 0.12f * (float)skill);
	if (p->script[i] & DOD_GRUNT_TURRET)
		gap = 0.25f + 0.2f * DodGrunt_Rand(p);	/* an MG42 on its bipod: short bursts, not aimed rifle shots */
	p->next_fire[i] = now + gap;
	p->stats.shots++;
	return 1;
}

float DodGrunt_HitChance(float dist, int skill)
{
	float c;
	if (skill < 0)
		skill = 0;
	if (skill > 3)
		skill = 3;
	c = 0.70f - dist / 1800.0f * 0.6f + 0.08f * (float)skill;
	return c < 0.05f ? 0.05f : (c > 0.95f ? 0.95f : c);
}

float DodGrunt_CampaignHitScale(int skill)
{
	/* the DoD grunt curve hits about 2 in 3 at 300 units; MOHAA's soldiers miss far more, by difficulty */
	return skill <= 1 ? 0.35f : (skill >= 3 ? 0.7f : 0.5f);
}

int DodGrunt_ShotHits(float dist, int skill, float roll)
{
	return roll < DodGrunt_HitChance(dist, skill);
}

int DodGrunt_Hurt(DodGruntPool *p, int i, int damage, float now)
{
	if (!alive(p, i))
		return 0;
	p->hp[i] = (short)(p->hp[i] - damage);
	if (p->hp[i] > 0)
		return 0;
	p->hp[i] = 0;
	p->state[i] = DOD_GRUNT_DEAD;
	p->target[i] = 0;
	p->order[i] = DOD_GRUNT_ORDER_NONE;
	/* a script actor stays dead: the mission counts its kills */
	p->respawn_at[i] = p->script[i] ? 1e30f : now + DOD_GRUNT_RESPAWN;
	p->stats.deaths++;
	return 1;
}

int DodGrunt_RespawnDue(const DodGruntPool *p, int i, float now)
{
	return p->state[i] == DOD_GRUNT_DEAD && p->respawn_at[i] <= now;
}

/* ---- script control ---- */

int DodGrunt_FreeScriptSlot(const DodGruntPool *p)
{
	int i;
	for (i = DOD_GRUNT_MAX - 1; i >= 0; i--)
		if (p->state[i] == DOD_GRUNT_FREE)
			return i;
	return -1;
}

void DodGrunt_SpawnScripted(DodGruntPool *p, int i, int team, float x, float y, float z, float yaw, float now)
{
	DodGrunt_Spawn(p, i, team, x, y, z, yaw, now, 0);
	p->script[i] = DOD_GRUNT_SCRIPTED | DOD_GRUNT_HEED_DISGUISE;
	p->state[i] = DOD_GRUNT_HOLD;
}

void DodGrunt_SetAI(DodGruntPool *p, int i, int on)
{
	if (on) {
		p->script[i] &= (unsigned char)~DOD_GRUNT_AI_OFF;
		return;
	}
	p->script[i] |= DOD_GRUNT_AI_OFF;
	p->script[i] &= (unsigned char)~DOD_GRUNT_ATTACK;
	p->target[i] = 0;
	if (alive(p, i) && p->order[i] == DOD_GRUNT_ORDER_NONE)
		p->state[i] = DOD_GRUNT_HOLD;
}

static short clamp_short(float v)
{
	return (short)(v > 32767.0f ? 32767 : (v < -32767.0f ? -32767 : (int)v));
}

void DodGrunt_SetParam(DodGruntPool *p, int i, int param, float value, float x, float y)
{
	if (param == DOD_GRUNT_LEASH && value < 0.0f) {
		/* MOHAA resetleash: same radius (MOHAA's 256 default when none was set), centred where it stands */
		if (!p->leash_r[i])
			p->leash_r[i] = 256;
		p->leash_x[i] = clamp_short(p->x[i]);
		p->leash_y[i] = clamp_short(p->y[i]);
		return;
	}
	if (value < 0.0f)
		value = 0.0f;
	switch (param) {
	case DOD_GRUNT_SIGHT_RANGE: p->sight[i] = clamp_short(value); break;
	case DOD_GRUNT_HEARING: p->hearing[i] = clamp_short(value); break;
	case DOD_GRUNT_FOV: p->fov[i] = (unsigned char)(value >= 360.0f ? 180 : value * 0.5f); break;
	case DOD_GRUNT_LEASH:
	case DOD_GRUNT_TETHER:
		if (param == DOD_GRUNT_LEASH)
			p->leash_r[i] = clamp_short(value);
		else if (!p->leash_r[i])
			p->leash_r[i] = 256;	/* MOHAA's default leash */
		if (param == DOD_GRUNT_LEASH && x == 0.0f && y == 0.0f) {
			x = p->x[i];
			y = p->y[i];
		}
		p->leash_x[i] = clamp_short(x);
		p->leash_y[i] = clamp_short(y);
		break;
	case DOD_GRUNT_MINDIST: p->mindist[i] = clamp_short(value); break;
	case DOD_GRUNT_MAXDIST: p->maxdist[i] = clamp_short(value); break;
	default: break;
	}
}

float DodGrunt_SightRange(const DodGruntPool *p, int i)
{
	return p->sight[i] > 0 ? (float)p->sight[i] : DOD_GRUNT_SIGHT;
}

float DodGrunt_HearingRange(const DodGruntPool *p, int i)
{
	return p->hearing[i] > 0 ? (float)p->hearing[i] : 300.0f;
}

float DodGrunt_FovCos(const DodGruntPool *p, int i)
{
	/* default about 70 degrees each side, as the grunts always looked */
	return p->fov[i] ? cosf((float)p->fov[i] * 0.017453293f) : 0.34f;
}

/* Inside the leash after a step to (nx, ny)? No leash: always. */
static int in_leash(const DodGruntPool *p, int i, float nx, float ny)
{
	float dx, dy, r;
	if (!p->leash_r[i])
		return 1;
	dx = nx - p->leash_x[i];
	dy = ny - p->leash_y[i];
	r = p->leash_r[i];
	return dx * dx + dy * dy <= r * r;
}

void DodGrunt_SetAttack(DodGruntPool *p, int i, int on)
{
	if (on) {
		p->script[i] |= DOD_GRUNT_ATTACK;
		p->script[i] &= (unsigned char)~DOD_GRUNT_AI_OFF;
	} else
		p->script[i] &= (unsigned char)~DOD_GRUNT_ATTACK;
}

void DodGrunt_OrderMove(DodGruntPool *p, int i, float x, float y, int run)
{
	if (!alive(p, i))
		return;
	p->script[i] &= (unsigned char)~DOD_GRUNT_SOFT_ORDER;	/* a script order is not a patrol walk */
	p->order[i] = (unsigned char)(run ? DOD_GRUNT_ORDER_RUN : DOD_GRUNT_ORDER_WALK);
	p->order_x[i] = x;
	p->order_y[i] = y;
	p->order_done[i] = 0;
	p->order_stall_at[i] = -1.0f;	/* the first Move after the order starts the clock */
	p->target[i] = 0;
	p->blocked[i] = 0;
	p->state[i] = run ? DOD_GRUNT_ADVANCE : DOD_GRUNT_WANDER;
	p->heading[i] = DodGrunt_YawTo(p->x[i], p->y[i], x, y);
}

void DodGrunt_OrderStop(DodGruntPool *p, int i)
{
	p->order[i] = DOD_GRUNT_ORDER_NONE;
	if (alive(p, i))
		p->state[i] = DOD_GRUNT_HOLD;
}

void DodGrunt_Face(DodGruntPool *p, int i, float tx, float ty)
{
	if (p->order[i] == DOD_GRUNT_ORDER_NONE)
		p->heading[i] = DodGrunt_YawTo(p->x[i], p->y[i], tx, ty);
}

int DodGrunt_TakeOrderDone(DodGruntPool *p, int i)
{
	if (!p->order_done[i])
		return 0;
	p->order_done[i] = 0;
	return 1;
}

void DodGrunt_ManTurret(DodGruntPool *p, int i, float gun_yaw, float arc_half, int mg_weapon)
{
	if (!alive(p, i))
		return;
	if (arc_half <= 0.0f)
		arc_half = DOD_GRUNT_TURRET_ARC;
	if (arc_half > 180.0f)
		arc_half = 180.0f;
	p->script[i] |= DOD_GRUNT_SCRIPTED | DOD_GRUNT_TURRET;
	p->script[i] &= (unsigned char)~(DOD_GRUNT_ATTACK | DOD_GRUNT_SOFT_ORDER);
	p->cover[i] = DOD_GRUNT_COVER_NONE;
	p->order[i] = DOD_GRUNT_ORDER_NONE;
	p->heading[i] = gun_yaw;
	p->yaw[i] = gun_yaw;
	DodGrunt_SetParam(p, i, DOD_GRUNT_LEASH, DOD_GRUNT_TURRET_LEASH, 0.0f, 0.0f);
	DodGrunt_SetParam(p, i, DOD_GRUNT_FOV, arc_half * 2.0f, 0.0f, 0.0f);
	if (mg_weapon >= 0)
		p->gun[i] = (unsigned char)(mg_weapon + 1);
	if (p->state[i] != DOD_GRUNT_SHOOT)
		p->state[i] = DOD_GRUNT_HOLD;
}

float DodGrunt_LookYaw(const DodGruntPool *p, int i)
{
	return (p->script[i] & DOD_GRUNT_TURRET) ? p->heading[i] : p->yaw[i];
}

float DodGrunt_AccuracyScale(const DodGruntPool *p, int i)
{
	float f;
	if (!p->accuracy[i])
		return 1.0f;
	f = (float)(p->accuracy[i] - 1) / 50.0f;
	return f < 0.2f ? 0.2f : (f > 2.0f ? 2.0f : f);
}
