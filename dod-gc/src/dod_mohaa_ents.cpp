/* dod_mohaa_ents.cpp - the HL1SDK side of the MOHAA script binding (see dod_mohaa.h). */
#include "extdll.h"
#include "util.h"
#include "cbase.h"
#include "player.h"
#include "gamerules.h"
#include "dod_game.h"
#include "dod_runtime.h"
#include "dod_mohaa.h"
#include "dod_mohaa_ents.h"
#include "shake.h"

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

/* Script memory cap in KiB. MEM1 is tight on GameCube (see docs/MEMORY.md); a level whose
 * scripts do not fit is refused cleanly at load instead of starving the engine. */
static cvar_t mohaa_script_kb = { "mohaa_script_kb", "384", FCVAR_SERVER };
static int g_mohaa_cvar_registered;

/* id = edict index (12 bits) | serial number (19 bits): a freed and reused edict does
 * not answer for an old script reference. Bit 31 stays clear: DOD_MOHAA_NODE_ID marks a path node. */
static uint32_t IdFor( edict_t *e )
{
	if( !e || e->free )
		return 0;
	return (uint32_t)ENTINDEX( e ) | ( (uint32_t)( e->serialnumber & 0x7FFFF ) << 12 );
}

static edict_t *EdictFor( uint32_t id )
{
	int index = (int)( id & 0xFFF );
	if( !id || index <= 0 || index >= gpGlobals->maxEntities )
		return NULL;
	edict_t *e = INDEXENT( index );
	if( !e || e->free || (uint32_t)( e->serialnumber & 0x7FFFF ) != ( id >> 12 ) || !e->pvPrivateData )
		return NULL;
	return e;
}

static char *M_Load( const char *path, size_t *len )
{
	int n = 0;
	byte *data = LOAD_FILE_FOR_ME( (char *)path, &n );
	if( !data )
		return NULL;
	*len = (size_t)n;
	return (char *)data;
}

static void M_Free( char *text )
{
	FREE_FILE( text );
}

static void M_Print( int channel, const char *text )
{
	switch( channel )
	{
	case DOD_MOHAA_PRINT_HUD:
		UTIL_ClientPrintAll( HUD_PRINTTALK, text );
		break;
	case DOD_MOHAA_PRINT_CENTER:
		UTIL_ClientPrintAll( HUD_PRINTCENTER, text );
		break;
	case DOD_MOHAA_PRINT_ERROR:
		ALERT( at_console, "%s", text );
		break;
	default:
		ALERT( at_aiconsole, "%s", text );
		break;
	}
}

static int M_Find( const char *name, uint32_t *ids, int max )
{
	int n = 0;
	edict_t *e = NULL;
	while( !FNullEnt( e = FIND_ENTITY_BY_TARGETNAME( e, name ) ) )
	{
		if( n < max )
			ids[n] = IdFor( e );
		n++;
	}
	/* MOHAA's "$player" is the (first) player, who has no targetname in GoldSrc */
	if( !n && !strcmp( name, "player" ) )
	{
		CBaseEntity *p = UTIL_PlayerByIndex( 1 );
		if( p && max > 0 )
			ids[0] = IdFor( p->edict() );
		n = p ? 1 : 0;
	}
	return n;
}

static int M_Valid( uint32_t id )
{
	return EdictFor( id ) != NULL;
}

static void M_GetVec( uint32_t id, int what, float out[3] )
{
	edict_t *e = EdictFor( id );
	Vector v = g_vecZero;
	if( e )
		v = what == DOD_MOHAA_ANGLES ? e->v.angles : e->v.origin;
	out[0] = v.x;
	out[1] = v.y;
	out[2] = v.z;
}

static void M_SetVec( uint32_t id, int what, const float v[3] )
{
	edict_t *e = EdictFor( id );
	if( !e )
		return;
	if( what == DOD_MOHAA_ANGLES )
		e->v.angles = Vector( v[0], v[1], v[2] );
	else
		UTIL_SetOrigin( VARS( e ), Vector( v[0], v[1], v[2] ) );
}

static float M_GetHealth( uint32_t id )
{
	edict_t *e = EdictFor( id );
	return e ? e->v.health : 0.0f;
}

static void M_SetHealth( uint32_t id, float health )
{
	edict_t *e = EdictFor( id );
	if( e )
		e->v.health = health;
}

static const char *M_GetStr( uint32_t id, int what )
{
	edict_t *e = EdictFor( id );
	if( !e )
		return "";
	string_t s = what == DOD_MOHAA_CLASSNAME ? e->v.classname : what == DOD_MOHAA_MODEL ? e->v.model : e->v.targetname;
	return s ? STRING( s ) : "";
}

static void M_SetTargetname( uint32_t id, const char *name )
{
	edict_t *e = EdictFor( id );
	if( e )
		e->v.targetname = ALLOC_STRING( name );
}

static void M_SetFlag( uint32_t id, int flag, int on )
{
	edict_t *e = EdictFor( id );
	if( !e )
		return;
	if( flag == DOD_MOHAA_HIDDEN )
	{
		if( on )
			e->v.effects |= EF_NODRAW;
		else
			e->v.effects &= ~EF_NODRAW;
		return;
	}
	if( on )
		e->v.solid = SOLID_NOT;
	else
	{
		const char *model = e->v.model ? STRING( e->v.model ) : "";
		e->v.solid = model[0] == '*' ? SOLID_BSP : SOLID_BBOX;
	}
	UTIL_SetOrigin( VARS( e ), e->v.origin );	/* relink with the new solidity */
}

static void M_Remove( uint32_t id )
{
	edict_t *e = EdictFor( id );
	if( e && DodGrunts_ScriptRemove( e ) )
		return;	/* an actor: its grunt slot goes with it */
	CBaseEntity *ent = e ? CBaseEntity::Instance( e ) : NULL;
	if( ent && !ent->IsPlayer() )
		UTIL_Remove( ent );
}

static void M_SetVelocity( uint32_t id, const float vel[3], const float avel[3] )
{
	edict_t *e = EdictFor( id );
	if( !e )
		return;
	/* brush entities (func_wall, doors) are pushers; point entities fly through */
	if( e->v.movetype == MOVETYPE_NONE )
		e->v.movetype = e->v.solid == SOLID_BSP ? MOVETYPE_PUSH : MOVETYPE_NOCLIP;
	e->v.velocity = Vector( vel[0], vel[1], vel[2] );
	e->v.avelocity = Vector( avel[0], avel[1], avel[2] );
}

static void M_UseTargets( const char *targetname )
{
	FireTargets( targetname, NULL, NULL, USE_TOGGLE, 0 );
}

/* A MOHAA AI soldier: "spawn actor ..." or "spawn models/human/<who>.tik ...". */
static int IsActorClass( const char *classname )
{
	return !strcmp( classname, "actor" ) || !strncmp( classname, "models/human/", 13 ) || !strncmp( classname, "human/", 6 );
}

/* Every soldier this binding put in the pool, with its side, so a full pool can make room (see SpawnActorAt). */
static struct { uint32_t id; int team; } g_actors[64];
static void ActorWait( int team, const Vector &origin, float yaw, const char *name );

static void ActorTrack( edict_t *e, int team )
{
	const uint32_t id = IdFor( e );
	for( int k = 0; k < 64; k++ )
		if( !g_actors[k].id || !EdictFor( g_actors[k].id ) ) {
			g_actors[k].id = id;
			g_actors[k].team = team;
			return;
		}
}

/* Make room for a soldier the script needs now: the living soldier with no name farthest from every player goes back
 * to the waiting list (scripts cannot address it, so nothing notices) and gives up its slot. 0: none to move. */
static int ActorMakeRoom( void )
{
	int best = -1;
	float best_d = -1.0f;
	for( int k = 0; k < 64; k++ ) {
		edict_t *e = g_actors[k].id ? EdictFor( g_actors[k].id ) : NULL;
		if( !e || e->v.targetname || e->v.health <= 0 )
			continue;
		float nearest = 1e9f;
		for( int p = 1; p <= gpGlobals->maxClients; p++ ) {
			edict_t *pe = INDEXENT( p );
			if( pe && !pe->free && ( pe->v.flags & FL_CLIENT ) )
				nearest = fminf( nearest, ( pe->v.origin - e->v.origin ).Length() );
		}
		if( nearest > best_d ) {
			best = k;
			best_d = nearest;
		}
	}
	if( best < 0 )
		return 0;
	edict_t *e = EdictFor( g_actors[best].id );
	ActorWait( g_actors[best].team, e->v.origin - Vector( 0, 0, 36 ), e->v.angles.y, NULL );
	g_actors[best].id = 0;
	return DodGrunts_ScriptRemove( e );
}

/* must: the script addresses this soldier (it has a name, or the script spawned it), so it takes an unnamed
 * soldier's slot when the pool is full rather than wait */
static edict_t *SpawnActorAt( int team, const Vector &origin, float yaw, const char *targetname, int must = 0 )
{
	edict_t *e = DodGrunts_ScriptSpawn( team, origin, yaw );
	if( !e && ( must || ( targetname && targetname[0] ) ) && ActorMakeRoom() )
		e = DodGrunts_ScriptSpawn( team, origin, yaw );
	if( !e )
		return NULL;
	if( targetname && targetname[0] )
		e->v.targetname = ALLOC_STRING( targetname );
	ActorTrack( e, team );
	return e;
}

static uint32_t SpawnActor( const char *classname, const char *const *keys, const char *const *values, int count )
{
	Vector origin = g_vecZero;
	float yaw = 0.0f;
	const char *targetname = NULL;
	/* German models play the Axis, everyone else the Allies (MOHAA's own split is by model too) */
	int team = strstr( classname, "german" ) ? DOD_TEAM_AXIS : DOD_TEAM_ALLIES;
	for( int i = 0; i < count; i++ ) {
		if( !strcmp( keys[i], "origin" ) )
			sscanf( values[i], "%f %f %f", &origin.x, &origin.y, &origin.z );
		else if( !strcmp( keys[i], "angle" ) )
			yaw = (float)atof( values[i] );
		else if( !strcmp( keys[i], "angles" ) )
			sscanf( values[i], "%*f %f", &yaw );
		else if( !strcmp( keys[i], "targetname" ) )
			targetname = values[i];
		else if( !strcmp( keys[i], "model" ) && strstr( values[i], "german" ) )
			team = DOD_TEAM_AXIS;
	}
	return IdFor( SpawnActorAt( team, origin, yaw, targetname, 1 ) );
}

/* Soldiers that found the grunt pool full (MOHAA maps place more than its 48 slots: m1l1 has 54). They wait here
 * and come in near a player as slots free up; a soldier dead for MOHAA_CORPSE_SECONDS gives its slot back while
 * any wait. */
#define MOHAA_WAITING_MAX 64
#define MOHAA_CORPSE_SECONDS 20.0f
static struct { int team; Vector origin; float yaw; string_t name; } g_waiting[MOHAA_WAITING_MAX];
static int g_nwaiting;
static struct { uint32_t id; float at; } g_dead[48];
static float g_next_waiting_check;

static void ActorWait( int team, const Vector &origin, float yaw, const char *name )
{
	if( g_nwaiting >= MOHAA_WAITING_MAX ) {
		ALERT( at_console, "mohaa_actor %s: dropped, %d soldiers already wait for a slot\n", name ? name : "", g_nwaiting );
		return;
	}
	g_waiting[g_nwaiting].team = team;
	g_waiting[g_nwaiting].origin = origin;
	g_waiting[g_nwaiting].yaw = yaw;
	g_waiting[g_nwaiting].name = name && name[0] ? ALLOC_STRING( name ) : 0;
	g_nwaiting++;
}

static void ActorDied( edict_t *e )
{
	const uint32_t id = IdFor( e );
	for( int k = 0; k < 48; k++ )
		if( !g_dead[k].id || !EdictFor( g_dead[k].id ) ) {
			g_dead[k].id = id;
			g_dead[k].at = gpGlobals->time;
			return;
		}
}

/* Twice a second while soldiers wait: free old corpses' slots, then bring in the waiting soldier nearest a player. */
static void ActorsWaitingThink( void )
{
	if( !g_nwaiting || gpGlobals->time < g_next_waiting_check )
		return;
	g_next_waiting_check = gpGlobals->time + 0.5f;
	for( int k = 0; k < 48; k++ ) {
		edict_t *e = g_dead[k].id ? EdictFor( g_dead[k].id ) : NULL;
		if( !e ) {
			g_dead[k].id = 0;
			continue;
		}
		if( gpGlobals->time - g_dead[k].at >= MOHAA_CORPSE_SECONDS ) {
			g_dead[k].id = 0;
			DodGrunts_ScriptRemove( e );
		}
	}
	int best = -1;
	float best_d = 0.0f;
	for( int w = 0; w < g_nwaiting; w++ ) {
		for( int p = 1; p <= gpGlobals->maxClients; p++ ) {
			edict_t *pe = INDEXENT( p );
			if( !pe || pe->free || !( pe->v.flags & FL_CLIENT ) || pe->v.health <= 0 )
				continue;
			const float d = ( pe->v.origin - g_waiting[w].origin ).Length();
			if( best < 0 || d < best_d ) {
				best = w;
				best_d = d;
			}
		}
	}
	if( best < 0 )
		return;
	const char *name = g_waiting[best].name ? STRING( g_waiting[best].name ) : NULL;
	if( !SpawnActorAt( g_waiting[best].team, g_waiting[best].origin, g_waiting[best].yaw, name ) )
		return;	/* still full */
	ALERT( at_console, "mohaa_actor %s: in from the waiting list (%d left)\n", name ? name : "", g_nwaiting - 1 );
	g_waiting[best] = g_waiting[--g_nwaiting];
}

/* A soldier placed in the map: mohaa-gc's converter writes MOHAA actors as mohaa_actor (origin at the feet, angle,
 * targetname, model). The game rules (and so the grunt pool and the script) exist before the map's entities spawn, so
 * it becomes a script grunt right here and the placeholder goes; "$name" in the script then finds the grunt. */
class CMohaaActor : public CPointEntity
{
public:
	void Precache( void ) { DodGrunts_PrecacheBodies(); }
	void Spawn( void )
	{
		Precache();
		const char *model = STRING( pev->model );
		const int team = strstr( model, "german" ) ? DOD_TEAM_AXIS : DOD_TEAM_ALLIES;
		pev->model = 0;	/* a .tik name, never a model the engine has */
		const char *name = pev->targetname ? STRING( pev->targetname ) : NULL;
		if( !SpawnActorAt( team, pev->origin, pev->angles.y, name ) )
			ActorWait( team, pev->origin, pev->angles.y, name );
		pev->targetname = 0;	/* the grunt answers to the name now */
		UTIL_Remove( this );
	}
};
LINK_ENTITY_TO_CLASS( mohaa_actor, CMohaaActor )

/* A soldier can walk from a to b (feet origins): the crouch-sized hull, lifted so 18-unit steps pass under it,
 * clears the world. Doors and other brush entities do not spawn until after this runs, so they never cut a link. */
static int M_Walkable( const float a[3], const float b[3] )
{
	TraceResult tr;
	UTIL_TraceHull( Vector( a[0], a[1], a[2] + 37.0f ), Vector( b[0], b[1], b[2] + 37.0f ), ignore_monsters, head_hull, NULL, &tr );
	return !tr.fStartSolid && tr.flFraction >= 1.0f;
}

static const char *M_GetCvar( const char *name )
{
	return CVAR_GET_STRING( name );
}

static void M_Fade( float seconds, float r, float g, float b, float alpha, int out )
{
	/* fade out holds the colour until a fade in; fade in starts from it */
	UTIL_ScreenFadeAll( Vector( r * 255.0f, g * 255.0f, b * 255.0f ), seconds, 0.0f, (int)( alpha * 255.0f ),
		out ? FFADE_OUT | FFADE_STAYOUT : FFADE_IN );
}

static int M_Actor( uint32_t id, int order, const float pos[3] )
{
	edict_t *e = EdictFor( id );
	return e ? DodGrunts_ScriptOrder( e, order, pos ) : 0;
}

static uint32_t M_Spawn( const char *classname, const char *const *keys, const char *const *values, int count )
{
	if( IsActorClass( classname ) )
		return SpawnActor( classname, keys, values, count );
	/* MOHAA's script helpers have no GoldSrc class: a point entity holds their place */
	if( !strcmp( classname, "script_model" ) || !strcmp( classname, "script_origin" ) || !strcmp( classname, "script_object" ) )
		classname = "info_target";
	edict_t *e = CREATE_NAMED_ENTITY( ALLOC_STRING( classname ) );
	if( FNullEnt( e ) ) {
		/* a MOHAA class GoldSrc lacks (trigger_save, animate/..., ...): a point entity still answers to its name */
		classname = "info_target";
		e = CREATE_NAMED_ENTITY( ALLOC_STRING( classname ) );
		if( FNullEnt( e ) )
			return 0;
	}
	for( int i = 0; i < count; i++ )
	{
		if( !strcmp( keys[i], "model" ) )
			continue;	/* MOHAA .tik models are not converted yet; an unprecached model would abort the server */
		KeyValueData kvd;
		kvd.szClassName = (char *)classname;
		kvd.szKeyName = (char *)keys[i];
		kvd.szValue = (char *)values[i];
		kvd.fHandled = FALSE;
		DispatchKeyValue( e, &kvd );
	}
	if( DispatchSpawn( e ) < 0 )
		return 0;
	return IdFor( e );
}

static void M_Precache( const char *sample )
{
	/* the table outlives this call only as long as the level: give the engine its own copy */
	PRECACHE_SOUND( (char *)STRING( ALLOC_STRING( sample ) ) );
}

static void M_Sound( uint32_t id, const char *sample, int loop, float volume, float attn, int channel )
{
	edict_t *e = EdictFor( id );
	if( !e )
		return;
	if( loop < 0 ) {
		STOP_SOUND( e, CHAN_STATIC, sample );
		return;
	}
	int chan = CHAN_AUTO;
	if( loop )
		chan = CHAN_STATIC;	/* repeats by the wav's own loop marker */
	else if( channel == DOD_MOHAA_CHAN_VOICE )
		chan = CHAN_VOICE;
	else if( channel == DOD_MOHAA_CHAN_ITEM )
		chan = CHAN_ITEM;
	else if( channel == DOD_MOHAA_CHAN_BODY )
		chan = CHAN_BODY;
	else if( channel == DOD_MOHAA_CHAN_WEAPON )
		chan = CHAN_WEAPON;
	EMIT_SOUND_DYN( e, chan, sample, volume, attn, 0, PITCH_NORM );
}

/* Background music: what should play now, and which clients have been told. Xash's "music <intro> [loop]" streams
 * the PCM wavs mohaa-gc tools/music.py writes; "music" alone stops. A player who joins later is told on the next
 * think, so everyone hears the same mood. */
static char g_music_intro[96], g_music_loop[96];
static int g_music_serial = 1;
static int g_music_sent[33];

static void M_Music( const char *intro, const char *loop )
{
	snprintf( g_music_intro, sizeof( g_music_intro ), "%s", intro ? intro : "" );
	snprintf( g_music_loop, sizeof( g_music_loop ), "%s", intro && loop ? loop : "" );
	g_music_serial++;
}

static void MusicSend( void )
{
	for( int k = 1; k <= gpGlobals->maxClients && k < 33; k++ ) {
		edict_t *e = INDEXENT( k );
		if( !e || e->free || !e->pvPrivateData || !( e->v.flags & FL_CLIENT ) || ( e->v.flags & FL_FAKECLIENT ) ) {
			g_music_sent[k] = 0;	/* an empty slot: whoever takes it next hears the music from the start */
			continue;
		}
		if( g_music_sent[k] == g_music_serial )
			continue;
		if( g_music_sent[k] || g_music_intro[0] ) {
			char cmd[224];
			if( g_music_intro[0] )
				snprintf( cmd, sizeof( cmd ), "music \"%s\" \"%s\"\n", g_music_intro, g_music_loop );
			else
				snprintf( cmd, sizeof( cmd ), "music\n" );
			CLIENT_COMMAND( e, cmd );
		}
		g_music_sent[k] = g_music_serial;
	}
}

void DodGC_MohaaLevelInit( void )
{
	if( !g_mohaa_cvar_registered )
	{
		CVAR_REGISTER( &mohaa_script_kb );
		g_mohaa_cvar_registered = 1;
	}
	DodMohaaBackend b;
	memset( &b, 0, sizeof( b ) );
	b.load_file = M_Load;
	b.free_file = M_Free;
	b.print = M_Print;
	b.find = M_Find;
	b.valid = M_Valid;
	b.get_vec = M_GetVec;
	b.set_vec = M_SetVec;
	b.get_health = M_GetHealth;
	b.set_health = M_SetHealth;
	b.get_str = M_GetStr;
	b.set_targetname = M_SetTargetname;
	b.set_flag = M_SetFlag;
	b.remove = M_Remove;
	b.set_velocity = M_SetVelocity;
	b.use_targets = M_UseTargets;
	b.spawn = M_Spawn;
	b.sound = M_Sound;
	b.precache_sound = M_Precache;
	b.actor = M_Actor;
	b.music = M_Music;
	if( g_music_intro[0] )
		M_Music( NULL, NULL );	/* the last map's music stops unless this map starts its own */
	b.walkable = M_Walkable;
	b.get_cvar = M_GetCvar;
	b.fade = M_Fade;
	g_nwaiting = 0;	/* the last map's waiting soldiers went with it */
	memset( g_actors, 0, sizeof( g_actors ) );
	memset( g_dead, 0, sizeof( g_dead ) );
	g_next_waiting_check = 0.0f;
	size_t budget = (size_t)CVAR_GET_FLOAT( "mohaa_script_kb" ) * 1024u;
	if( Dod_MohaaLevelInit( &b, STRING( gpGlobals->mapname ), gpGlobals->time, budget ) ) {
		DodGrunts_PrecacheBodies();	/* the mission's soldiers wear the sides' player bodies */
		ALERT( at_console, "mohaa: running maps/%s.scr (budget %u KiB)\n", STRING( gpGlobals->mapname ),
			(unsigned)( budget / 1024u ) );
	}
}

void DodGC_MohaaThink( void )
{
	Dod_MohaaThink( gpGlobals->time );
	MusicSend();
	ActorsWaitingThink();
}

void DodGC_MohaaEntityEvent( edict_t *e, const char *event )
{
	uint32_t id = IdFor( e );
	if( id && !strcmp( event, "death" ) )
		ActorDied( e );
	if( id )
		Dod_MohaaNotify( id, event );
	/* mohaa-gc's converter puts a MOHAA trigger's setthread label in netname */
	if( id && !strcmp( event, "trigger" ) && e->v.netname && !strncmp( STRING( e->v.classname ), "trigger_", 8 ) )
		Dod_MohaaRunThread( STRING( e->v.netname ), id );
}
