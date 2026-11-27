/* dod_mohaa_ents.cpp - the HL1SDK side of the MOHAA script binding (see dod_mohaa.h). */
#include "extdll.h"
#include "util.h"
#include "cbase.h"
#include "player.h"
#include "weapons.h"
#include "gamerules.h"
#include "dod_game.h"
#include "dod_runtime.h"
#include "dod_mohaa.h"
#include "dod_mohaa_ents.h"
#include "shake.h"
#include "studio.h"

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "dod_grunts.h"

/* Script memory cap in KiB. MEM1 is tight on GameCube (see docs/MEMORY.md); a level whose
 * scripts do not fit is refused cleanly at load instead of starving the engine. */
static cvar_t mohaa_script_kb = { "mohaa_script_kb", "384", FCVAR_SERVER };
/* Probe aid: "mohaa_probe_goto <targetname>" (or a probe disc's maps/<map>.goto naming it, since a menu boot runs
 * no config) puts the player 700 units in front of that entity, facing it, two seconds into the level, so a
 * headless run can film a spot the mission takes minutes to reach. Retail discs carry neither. */
static cvar_t mohaa_probe_goto = { "mohaa_probe_goto", "", FCVAR_SERVER };
static int g_probe_goto_done;
static float g_probe_fire_from, g_probe_fire_until;
static int g_mohaa_cvar_registered;
static int gmsgMohaaHudDraw;
static int gmsgMohaaCompass;

void DodGC_MohaaRegisterHudMessages( void )
{
	if( !gmsgMohaaHudDraw ) gmsgMohaaHudDraw = REG_USER_MSG( "MohaaHudDraw", -1 );
	if( !gmsgMohaaCompass ) gmsgMohaaCompass = REG_USER_MSG( "MohaaCompass", -1 );
}

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

static edict_t *ActorWakeByName( const char *name );

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
	/* A map soldier still waiting for a pool slot answers to its name too: the script needs it now (m5l1b's
	 * cabinet.scr turns its hidden soldiers into spawners at the start), so it comes in, taking an unnamed soldier's
	 * slot if it must. */
	if( !n && name && name[0] && strcmp( name, "player" ) )
	{
		edict_t *in = ActorWakeByName( name );
		if( in ) {
			if( max > 0 )
				ids[0] = IdFor( in );
			n = 1;
		}
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

/* Scripted TIKI models baked for this map and precached from its .models manifest. */
#define MOHAA_SCRIPT_MODEL_LIMIT 32
static char g_mohaa_script_models[MOHAA_SCRIPT_MODEL_LIMIT][128];
static int g_mohaa_script_model_count;

static int ScriptModelPrecached( const char *path )
{
	for( int i = 0; i < g_mohaa_script_model_count; i++ )
		if( !strcmp( g_mohaa_script_models[i], path ) )
			return 1;
	return 0;
}

static int M_PrecacheModel( const char *path )
{
	if( !path || strncmp( path, "models/", 7 ) || strlen( path ) < 12 ||
	    strcmp( path + strlen( path ) - 4, ".mdl" ) || strstr( path, ".." ) ||
	    g_mohaa_script_model_count >= MOHAA_SCRIPT_MODEL_LIMIT )
		return 0;
	for( int i = 0; i < g_mohaa_script_model_count; i++ )
		if( !strcmp( g_mohaa_script_models[i], path ) )
			return 1;
	if( PRECACHE_MODEL( (char *)path ) <= 0 )
		return 0;
	strncpy( g_mohaa_script_models[g_mohaa_script_model_count], path,
	         sizeof( g_mohaa_script_models[0] ) - 1 );
	g_mohaa_script_model_count++;
	return 1;
}

static int M_SetAnimation( uint32_t id, const char *alias );
static const char *ActorTik( uint32_t id );

static int M_SetModel( uint32_t id, const char *tiki )
{
	edict_t *e = EdictFor( id );
	const char *classname;
	const int actor = ActorTik( id ) != NULL;
	char path[128];
	size_t n;
	if( !e || !tiki )
		return 0;
	classname = STRING( e->v.classname );
	if( strcmp( classname, "mohaa_script_model" ) && !actor )
		return 0;
	if( !strncmp( tiki, "models/", 7 ) )
		snprintf( path, sizeof( path ), "%s", tiki );
	else
		snprintf( path, sizeof( path ), "models/%s", tiki );
	n = strlen( path );
	/* a TIKI name maps to its baked .mdl; a model a script already names as .mdl passes too (Codex) */
	if( n < 4 )
		return 0;
	if( !strcmp( path + n - 4, ".tik" ) )
		memcpy( path + n - 4, ".mdl", 5 );
	else if( strcmp( path + n - 4, ".mdl" ) )
		return 0;
	for( char *p = path; *p; p++ )
		*p = (char)tolower( (unsigned char)*p );
	for( int i = 0; i < g_mohaa_script_model_count; i++ )
		if( !strcmp( g_mohaa_script_models[i], path ) ) {
			SET_MODEL( e, path );
			e->v.sequence = 0;
			e->v.frame = 0;
			e->v.framerate = 0.0f; /* M_SetAnimation starts the TIKI's idle sequence below */
			e->v.animtime = gpGlobals->time;
			if( actor ) {
				studiohdr_t *header = (studiohdr_t *)GET_MODEL_PTR( e );
				if( header )
					for( int group = 0; group < header->numbodyparts && group < 31; group++ )
						((CBaseAnimating *)e->pvPrivateData)->SetBodygroup( group, 1 );
			} else {
				M_SetAnimation( id, "idle" ); /* applies the TIKI init surface state too */
			}
			return 1;
		}
	return 0; /* tag-carrier TIKIs have no drawable MDL in the manifest */
}

class CMohaaScriptModel : public CBaseAnimating
{
public:
	int SetScriptAnimation( const char *alias )
	{
		const int sequence = LookupSequence( alias );
		if( sequence < 0 )
			return 0;
		pev->sequence = sequence;
		pev->frame = 0;
		pev->framerate = 1.0f;
		studiohdr_t *header = (studiohdr_t *)GET_MODEL_PTR( ENT( pev ) );
		if( header && sequence < header->numseq )
		{
			mstudioseqdesc_t *sequences = (mstudioseqdesc_t *)( (byte *)header + header->seqindex );
			/* Script TIKI MDLs store their per-alias visible-surface mask in activity. */
			const unsigned int visible = (unsigned int)sequences[sequence].activity;
			const int groups = header->numbodyparts < 31 ? header->numbodyparts : 31;
			for( int group = 0; group < groups; group++ )
				SetBodygroup( group, ( visible >> group ) & 1 );
		}
		ResetSequenceInfo();
		return 1;
	}

	void Spawn( void )
	{
		pev->movetype = MOVETYPE_NONE;
		pev->solid = SOLID_NOT;
		pev->sequence = 0;
		pev->frame = 0;
		pev->framerate = 0.0f;
		UTIL_SetOrigin( pev, pev->origin );
	}
};
LINK_ENTITY_TO_CLASS( mohaa_script_model, CMohaaScriptModel )

static int M_SetAnimation( uint32_t id, const char *alias )
{
	edict_t *e = EdictFor( id );
	if( !e || !alias )
		return 0;
	if( !strcmp( STRING( e->v.classname ), "mohaa_script_model" ) ) {
		CMohaaScriptModel *model = (CMohaaScriptModel *)e->pvPrivateData;
		return model ? model->SetScriptAnimation( alias ) : 0;
	}
	if( ActorTik( id ) ) {
		CBaseAnimating *model = (CBaseAnimating *)e->pvPrivateData;
		const int sequence = model ? model->LookupSequence( alias ) : -1;
		if( sequence < 0 )
			return 0;
		e->v.sequence = sequence;
		e->v.frame = 0;
		e->v.framerate = 1.0f;
		e->v.animtime = gpGlobals->time;
		studiohdr_t *header = (studiohdr_t *)GET_MODEL_PTR( e );
		if( header && sequence < header->numseq ) {
			mstudioseqdesc_t *sequences = (mstudioseqdesc_t *)( (byte *)header + header->seqindex );
			const unsigned int visible = (unsigned int)sequences[sequence].activity;
			for( int group = 0; group < header->numbodyparts && group < 31; group++ )
				model->SetBodygroup( group, ( visible >> group ) & 1 );
		}
		model->ResetSequenceInfo();
		return 1;
	}
	return 0;
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

static void M_SetAmmo( uint32_t id, const char *category, int amount )
{
	static const struct { const char *category; const char *pool; } pools[] = {
		{ "rifle", "mohaa_rifle" }, { "smg", "mohaa_smg" },
		{ "pistol", "mohaa_pistol" }, { "mg", "mohaa_mg" },
		{ "heavy", "mohaa_heavy" }, { "agrenade", "Hand Grenade" },
		{ "grenade", "Hand Grenade" }, { "shotgun", "buckshot" }
	};
	edict_t *e = EdictFor( id );
	CBasePlayer *player = e ? (CBasePlayer *)CBaseEntity::Instance( e ) : NULL;
	const char *pool = NULL;
	int ammo_index, max_ammo = 254;
	size_t i;
	if( !player || !player->IsPlayer() || !category )
		return;
	for( i = 0; i < sizeof( pools ) / sizeof( pools[0] ); i++ )
		if( !strcmp( category, pools[i].category ) ) {
			pool = pools[i].pool;
			break;
		}
	if( !pool )
		return;
	ammo_index = player->GetAmmoIndex( pool );
	if( ammo_index < 0 || ammo_index >= MAX_AMMO_SLOTS )
		return;
	/* Keep the retail category's exact pool separate from similarly-caliber DoD weapons. */
	for( int slot = 0; slot < MAX_ITEM_TYPES; slot++ )
		for( CBasePlayerItem *item = player->m_rgpPlayerItems[slot]; item; item = item->m_pNext )
			if( item->pszAmmo1() && !strcmp( item->pszAmmo1(), pool ) &&
			    item->m_iId >= 0 && item->m_iId < MAX_WEAPONS ) {
				const int cap = CBasePlayerItem::ItemInfoArray[item->m_iId].iMaxAmmo1;
				if( cap > 0 && cap < max_ammo )
					max_ammo = cap;
			}
	if( amount < 0 ) amount = 0;
	if( amount > max_ammo ) amount = max_ammo;
	player->m_rgAmmo[ammo_index] = amount;
	player->m_rgAmmoLast[ammo_index] = -1; /* force AmmoX/HUD refresh on next player update */
}

static int M_EqualNoCase( const char *a, const char *b )
{
	if( !a || !b ) return 0;
	while( *a && *b ) {
		if( tolower( (unsigned char)*a ) != tolower( (unsigned char)*b ) ) return 0;
		a++; b++;
	}
	return *a == *b;
}

static int M_EqualNoCaseN( const char *a, const char *b, size_t n )
{
	if( !a || !b ) return 0;
	while( n-- ) {
		if( tolower( (unsigned char)*a ) != tolower( (unsigned char)*b ) ) return 0;
		if( !*a || !*b ) return 0;
		a++; b++;
	}
	return 1;
}

static const char *M_WeaponClassForTiki( const char *tiki )
{
	static const struct { const char *tiki; const char *classname; } items[] = {
		{ "colt45", "weapon_dod_colt" }, { "silencedpistol", "weapon_dod_colt" },
		{ "m1_garand", "weapon_dod_garand" }, { "m1garand", "weapon_dod_garand" },
		{ "m1carbine", "weapon_dod_garand" }, { "springfield", "weapon_dod_spring" },
		{ "thompsonsmg", "weapon_dod_thompson" }, { "thompson", "weapon_dod_thompson" },
		{ "mp40", "weapon_dod_mp40" }, { "bar", "weapon_dod_bar" },
		{ "browning", "weapon_dod_30cal" }, { "mg42", "weapon_dod_mg42" },
		{ "bazooka", "weapon_dod_bazooka" }, { "panzerschreck", "weapon_dod_pschreck" },
		{ "mp44", "weapon_dod_stg44" }, { "stg44", "weapon_dod_stg44" },
		{ "kar98", "weapon_dod_k98" }, { "kar98k", "weapon_dod_k98" },
		{ "kar98sniper", "weapon_dod_k98s" }, { "luger", "weapon_dod_luger" },
		{ "shotgun", "weapon_shotgun" },
		{ "m2frag_grenade_sp_start", "weapon_handgrenade" },
		{ "m2frag_grenade_sp", "weapon_handgrenade" },
		{ "steilhandgranate_start", "weapon_handgrenade" },
		{ "steilhandgranate", "weapon_handgrenade" }
	};
	const char *name = tiki, *base;
	size_t i, len;
	if( !name || !*name ) return NULL;
	base = strrchr( name, '/' );
	base = base ? base + 1 : name;
	len = strlen( base );
	if( len > 4 && !M_EqualNoCase( base + len - 4, ".tik" ) )
		return NULL;
	for( i = 0; i < sizeof( items ) / sizeof( items[0] ); i++ ) {
		const size_t item_len = strlen( items[i].tiki );
		if( len == item_len + 4 && M_EqualNoCaseN( base, items[i].tiki, item_len ) && M_EqualNoCase( base + item_len, ".tik" ) )
			return items[i].classname;
	}
	return NULL;
}

static void M_GiveItem( uint32_t id, const char *tiki )
{
	edict_t *e = EdictFor( id );
	CBasePlayer *player = e ? (CBasePlayer *)CBaseEntity::Instance( e ) : NULL;
	const char *classname = M_WeaponClassForTiki( tiki );
	if( !player || !player->IsPlayer() ) return;
	if( classname )
		player->GiveNamedItem( classname );
	else
		ALERT( at_console, "MOHAA item: unsupported retail weapon TIKI '%s'\n", tiki ? tiki : "" );
}

static void M_TakeAll( uint32_t id )
{
	edict_t *e = EdictFor( id );
	CBasePlayer *player = e ? (CBasePlayer *)CBaseEntity::Instance( e ) : NULL;
	if( player && player->IsPlayer() )
		player->RemoveAllItems( FALSE );
}

static const char *M_WeaponPoolForClass( const char *weapon_class )
{
	if( M_EqualNoCase( weapon_class, "pistol" ) ) return "mohaa_pistol";
	if( M_EqualNoCase( weapon_class, "rifle" ) ) return "mohaa_rifle";
	if( M_EqualNoCase( weapon_class, "smg" ) ) return "mohaa_smg";
	if( M_EqualNoCase( weapon_class, "mg" ) ) return "mohaa_mg";
	if( M_EqualNoCase( weapon_class, "heavy" ) ) return "mohaa_heavy";
	if( M_EqualNoCase( weapon_class, "grenade" ) || M_EqualNoCase( weapon_class, "agrenade" ) ) return "Hand Grenade";
	if( M_EqualNoCase( weapon_class, "shotgun" ) ) return "buckshot";
	return NULL;
}

static void M_UseWeaponClass( uint32_t id, const char *weapon_class )
{
	edict_t *e = EdictFor( id );
	CBasePlayer *player = e ? (CBasePlayer *)CBaseEntity::Instance( e ) : NULL;
	const char *pool = M_WeaponPoolForClass( weapon_class );
	if( !player || !player->IsPlayer() || !pool ) return;
	for( int slot = 0; slot < MAX_ITEM_TYPES; slot++ )
		for( CBasePlayerItem *item = player->m_rgpPlayerItems[slot]; item; item = item->m_pNext )
			if( item->pszAmmo1() && M_EqualNoCase( item->pszAmmo1(), pool ) ) {
				player->SelectItem( STRING( item->pev->classname ) );
				return;
			}
}

static const char *M_GetStr( uint32_t id, int what )
{
	edict_t *e = EdictFor( id );
	if( !e )
		return "";
	if( what == DOD_MOHAA_MODEL ) {
		const char *tik = ActorTik( id );
		if( tik )
			return tik;
	}
	string_t s = what == DOD_MOHAA_CLASSNAME ? e->v.classname : what == DOD_MOHAA_MODEL ? e->v.model :
		what == DOD_MOHAA_TARGET ? e->v.target : e->v.targetname;
	return s ? STRING( s ) : "";
}

static void M_SetTargetname( uint32_t id, const char *name )
{
	edict_t *e = EdictFor( id );
	if( e )
		e->v.targetname = ALLOC_STRING( name );
}

/* triggers a script made "nottriggerable" */
#define MOHAA_UNTRIGGERABLE_MAX 32
static uint32_t g_untriggerable[MOHAA_UNTRIGGERABLE_MAX];

static int Untriggerable( edict_t *e )
{
	const uint32_t id = IdFor( e );
	for( int k = 0; id && k < MOHAA_UNTRIGGERABLE_MAX; k++ )
		if( g_untriggerable[k] == id )
			return 1;
	return 0;
}

static void M_SetFlag( uint32_t id, int flag, int on )
{
	edict_t *e = EdictFor( id );
	if( !e )
		return;
	if( flag == DOD_MOHAA_UNTRIGGERABLE )
	{
		int free_row = -1;
		for( int k = 0; k < MOHAA_UNTRIGGERABLE_MAX; k++ ) {
			if( g_untriggerable[k] == id )
				g_untriggerable[k] = 0;
			if( free_row < 0 && ( !g_untriggerable[k] || !EdictFor( g_untriggerable[k] ) ) )
				free_row = k;
		}
		if( on && free_row >= 0 )
			g_untriggerable[free_row] = id;
		/* a touch trigger stops touching; trigger_use is only reached through USE, which skips it */
		if( FClassnameIs( &e->v, "trigger_multiple" ) || FClassnameIs( &e->v, "trigger_once" ) ) {
			e->v.solid = on ? SOLID_NOT : SOLID_TRIGGER;
			UTIL_SetOrigin( VARS( e ), e->v.origin );
		}
		return;
	}
	if( flag == DOD_MOHAA_HIDDEN )
	{
		if( on )
			e->v.effects |= EF_NODRAW;
		else
			e->v.effects &= ~EF_NODRAW;
		return;
	}
	if( flag == DOD_MOHAA_TAKEDAMAGE )
	{
		e->v.takedamage = on ? DAMAGE_YES : DAMAGE_NO;
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

/* Every soldier this binding put in the pool, with its side, so a full pool can make room (see SpawnActorAt), and
 * its MOHAA model (human/....tik): scripts read .model to spawn another like it (global/spawner.scr), and the
 * grunt's own model is a player body that is no actor class. */
static struct { uint32_t id; int team; string_t tik; } g_actors[64];
static void ActorWait( int team, const Vector &origin, float yaw, const char *name, uint32_t keys, string_t tik );
static void CrewWait( edict_t *actor, string_t gun );

static void ActorTrack( edict_t *e, int team, string_t tik )
{
	const uint32_t id = IdFor( e );
	for( int k = 0; k < 64; k++ )
		if( !g_actors[k].id || !EdictFor( g_actors[k].id ) ) {
			g_actors[k].id = id;
			g_actors[k].team = team;
			g_actors[k].tik = tik;
			return;
		}
}

/* the MOHAA model of a soldier this binding made, or NULL */
static const char *ActorTik( uint32_t id )
{
	for( int k = 0; k < 64; k++ )
		if( g_actors[k].id == id )
			return g_actors[k].tik ? STRING( g_actors[k].tik ) : NULL;
	return NULL;
}

/* a .tik name worth keeping as a soldier's model ("" and GoldSrc models are not) */
static string_t TikName( const char *model )
{
	return model && strstr( model, ".tik" ) ? ALLOC_STRING( model ) : 0;
}

/* Make room for a soldier the script needs now: the living soldier with no name farthest from every player goes back
 * to the waiting list (scripts cannot address it, so nothing notices) and gives up its slot. 0: none to move. */
static int g_make_room_named;	/* ActorWakeByName: a named soldier far away may give way too */
static void ActorWaitKeepTarget( string_t target );

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
	/* A script asked for a waiting soldier by name and no unnamed one can give way: the named soldier farthest from
	 * every player (at least 2500 units off, nowhere near the fight) goes back to the waiting list instead, keeping
	 * its name, keys and target; asking for it by name brings it back the same way. */
	if( best < 0 && g_make_room_named ) {
		for( int k = 0; k < 64; k++ ) {
			edict_t *e = g_actors[k].id ? EdictFor( g_actors[k].id ) : NULL;
			if( !e || !e->v.targetname || e->v.health <= 0 )
				continue;
			float nearest = 1e9f;
			for( int p = 1; p <= gpGlobals->maxClients; p++ ) {
				edict_t *pe = INDEXENT( p );
				if( pe && !pe->free && ( pe->v.flags & FL_CLIENT ) )
					nearest = fminf( nearest, ( pe->v.origin - e->v.origin ).Length() );
			}
			if( nearest >= 2500.0f && nearest > best_d ) {
				best = k;
				best_d = nearest;
			}
		}
	}
	if( best < 0 )
		return 0;
	edict_t *e = EdictFor( g_actors[best].id );
	const char *name = e->v.targetname ? STRING( e->v.targetname ) : NULL;
	const string_t target = e->v.target;
	ActorWait( g_actors[best].team, e->v.origin - Vector( 0, 0, 36 ), e->v.angles.y, name, g_actors[best].id, g_actors[best].tik );
	if( name ) {
		ActorWaitKeepTarget( target );
		ALERT( at_console, "mohaa_actor %s: back to the waiting list to make room\n", name );
	}
	g_actors[best].id = 0;
	return DodGrunts_ScriptRemove( e );
}

/* must: the script addresses this soldier (it has a name, or the script spawned it), so it takes an unnamed
 * soldier's slot when the pool is full rather than wait */
static edict_t *SpawnActorAt( int team, const Vector &origin, float yaw, const char *targetname, string_t tik, int must = 0 )
{
	edict_t *e = DodGrunts_ScriptSpawn( team, origin, yaw );
	if( !e && ( must || ( targetname && targetname[0] ) ) && ActorMakeRoom() )
		e = DodGrunts_ScriptSpawn( team, origin, yaw );
	if( !e )
		return NULL;
	if( targetname && targetname[0] )
		e->v.targetname = ALLOC_STRING( targetname );
	ActorTrack( e, team, tik );
	if( tik )
		M_SetModel( IdFor( e ), STRING( tik ) );
	return e;
}

static uint32_t SpawnActor( const char *classname, const char *const *keys, const char *const *values, int count )
{
	Vector origin = g_vecZero;
	float yaw = 0.0f;
	const char *targetname = NULL;
	string_t tik = TikName( classname );	/* "spawn human/german_afrika_private.tik" */
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
		else if( !strcmp( keys[i], "model" ) ) {
			if( strstr( values[i], "german" ) )
				team = DOD_TEAM_AXIS;
			if( strstr( values[i], ".tik" ) )
				tik = TikName( values[i] );
		}
	}
	return IdFor( SpawnActorAt( team, origin, yaw, targetname, tik, 1 ) );
}

/* Soldiers that found the grunt pool full (MOHAA maps can place more than its DOD_GRUNT_MAX slots). They wait here
 * and come in near a player as slots free up; a soldier dead for MOHAA_CORPSE_SECONDS gives its slot back while
 * any wait. */
#define MOHAA_WAITING_MAX 64
#define MOHAA_CORPSE_SECONDS 20.0f
static struct { int team; Vector origin; float yaw; string_t name; uint32_t park; string_t tik; string_t target; } g_waiting[MOHAA_WAITING_MAX];
static int g_nwaiting;

/* the soldier ActorWait just parked keeps its map target */
static void ActorWaitKeepTarget( string_t target )
{
	if( g_nwaiting > 0 )
		g_waiting[g_nwaiting - 1].target = target;
}
static uint32_t g_park_serial;

/* An id no entity has (edict index 0 is the world, never a soldier), to hold a waiting soldier's script variables
 * (its map # keys) until it gets a body. */
static uint32_t ParkId( void )
{
	g_park_serial = ( g_park_serial + 1 ) & 0x7FFFF;
	if( !g_park_serial )
		g_park_serial = 1;
	return g_park_serial << 12;
}
static struct { uint32_t id; float at; } g_dead[DOD_GRUNT_MAX];
static float g_next_waiting_check;

/* keys: the entity whose script variables go with the soldier (0: none) */
static void ActorWait( int team, const Vector &origin, float yaw, const char *name, uint32_t keys, string_t tik )
{
	if( g_nwaiting >= MOHAA_WAITING_MAX ) {
		ALERT( at_console, "mohaa_actor %s: dropped, %d soldiers already wait for a slot\n", name ? name : "", g_nwaiting );
		return;
	}
	g_waiting[g_nwaiting].park = 0;
	if( keys ) {
		g_waiting[g_nwaiting].park = ParkId();
		Dod_MohaaEntityMoved( keys, g_waiting[g_nwaiting].park );
	}
	g_waiting[g_nwaiting].team = team;
	g_waiting[g_nwaiting].origin = origin;
	g_waiting[g_nwaiting].yaw = yaw;
	g_waiting[g_nwaiting].name = name && name[0] ? ALLOC_STRING( name ) : 0;
	g_waiting[g_nwaiting].tik = tik;
	g_waiting[g_nwaiting].target = 0;
	g_nwaiting++;
}

static void ActorDied( edict_t *e )
{
	const uint32_t id = IdFor( e );
	for( int k = 0; k < DOD_GRUNT_MAX; k++ )
		if( !g_dead[k].id || !EdictFor( g_dead[k].id ) ) {
			g_dead[k].id = id;
			g_dead[k].at = gpGlobals->time;
			return;
		}
}

/* Twice a second while soldiers wait: free old corpses' slots, then bring in the waiting soldier nearest a player. */
/* Waiting soldier w gets a body (must: a script asked for it by name, so an unnamed soldier gives up its slot). */
static edict_t *ActorBringIn( int w, int must )
{
	const char *name = g_waiting[w].name ? STRING( g_waiting[w].name ) : NULL;
	edict_t *in = SpawnActorAt( g_waiting[w].team, g_waiting[w].origin, g_waiting[w].yaw, name, g_waiting[w].tik, must );
	if( !in )
		return NULL;	/* still full */
	if( g_waiting[w].target ) {
		/* a map soldier that waited keeps its map target: an MG42's crew still mans its gun */
		in->v.target = g_waiting[w].target;
		CrewWait( in, g_waiting[w].target );
	}
	if( g_waiting[w].park )
		Dod_MohaaEntityMoved( g_waiting[w].park, IdFor( in ) );
	ALERT( at_console, "mohaa_actor %s: in from the waiting list%s (%d left)\n", name ? name : "",
		must ? ", asked for by name" : "", g_nwaiting - 1 );
	g_waiting[w] = g_waiting[--g_nwaiting];
	return in;
}

static void ActorsWaitingThink( void )
{
	if( !g_nwaiting || gpGlobals->time < g_next_waiting_check )
		return;
	g_next_waiting_check = gpGlobals->time + 0.5f;
	for( int k = 0; k < DOD_GRUNT_MAX; k++ ) {
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
	ActorBringIn( best, 0 );
}

static edict_t *ActorWakeByName( const char *name )
{
	for( int w = 0; w < g_nwaiting; w++ )
		if( g_waiting[w].name && !strcmp( STRING( g_waiting[w].name ), name ) ) {
			g_make_room_named = 1;
			edict_t *in = ActorBringIn( w, 1 );
			g_make_room_named = 0;
			return in;
		}
	return NULL;
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
		const string_t tik = TikName( model );	/* the soldier answers .model with it */
		pev->model = 0;	/* a .tik name, never a model the engine has */
		const char *name = pev->targetname ? STRING( pev->targetname ) : NULL;
		edict_t *grunt = SpawnActorAt( team, pev->origin, pev->angles.y, name, tik );
		/* the soldier keeps the map's target ($guy.target: spotlight.scr finds a gunner's MG42 by it); a map actor
		 * that targets a turretweapon is its crew (m1l2a's and m1l2b's MG42 nests) */
		if( grunt && pev->target ) {
			grunt->v.target = pev->target;
			CrewWait( grunt, pev->target );
		}
		/* the map's # keys (#set, #friendtype ...) arrived on this placeholder: they go with the soldier */
		if( grunt )
			Dod_MohaaEntityMoved( IdFor( edict() ), IdFor( grunt ) );
		else
		{
			ActorWait( team, pev->origin, pev->angles.y, name, IdFor( edict() ), tik );
			if( g_nwaiting > 0 && pev->target )
				g_waiting[g_nwaiting - 1].target = pev->target;
		}
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

static void M_SetCvar( const char *name, const char *value )
{
	CVAR_SET_STRING( name, value );
}

static void M_Fade( float seconds, float r, float g, float b, float alpha, int out )
{
	/* fade out holds the colour until a fade in; fade in starts from it */
	UTIL_ScreenFadeAll( Vector( r * 255.0f, g * 255.0f, b * 255.0f ), seconds, 0.0f, (int)( alpha * 255.0f ),
		out ? FFADE_OUT | FFADE_STAYOUT : FFADE_IN );
}

/* ---- cutscenes (see "Cutscenes" in dod_mohaa.c) ---- */

static uint32_t g_locked_player;	/* held by physics_off / freezeplayer: no walking, no firing */
static int g_saved_movetype;
static string_t g_saved_viewmodel;	/* the weapon model, put away while the HUD's weapon part is hidden */
static int g_hud_hide;

static CBasePlayer *PlayerFor( uint32_t id )
{
	edict_t *e = EdictFor( id );
	CBaseEntity *ent = e ? CBaseEntity::Instance( e ) : NULL;
	return ent && ent->IsPlayer() ? (CBasePlayer *)ent : NULL;
}

static void M_PlayerLock( uint32_t id, int locked )
{
	CBasePlayer *pl = PlayerFor( id );
	if( !pl )
		return;
	if( locked && g_locked_player != id )
	{
		g_locked_player = id;
		g_saved_movetype = pl->pev->movetype;
		/* noclip: the script places them every frame, nothing pulls them down between; FL_FROZEN zeroes their
		 * move input (pm_shared) but leaves the view free, as MOHAA's physics_off does */
		pl->pev->movetype = MOVETYPE_NOCLIP;
		pl->pev->flags |= FL_FROZEN;
		pl->pev->velocity = g_vecZero;
	}
	else if( !locked && g_locked_player == id )
	{
		g_locked_player = 0;
		pl->pev->movetype = g_saved_movetype ? g_saved_movetype : MOVETYPE_WALK;
		pl->pev->flags &= ~FL_FROZEN;
		pl->pev->velocity = g_vecZero;
	}
}

static void M_PlacePlayer( uint32_t id, const float pos[3], int eye )
{
	CBasePlayer *pl = PlayerFor( id );
	if( !pl )
		return;
	Vector p( pos[0], pos[1], pos[2] );
	/* GoldSrc's player origin is the middle of the hull: eyes are view_ofs above it, feet mins.z below */
	p = eye ? p - pl->pev->view_ofs : p - Vector( 0, 0, pl->pev->mins.z );
	UTIL_SetOrigin( pl->pev, p );
	pl->pev->velocity = g_vecZero;
}

static void M_View( uint32_t id, const float a[3], int add )
{
	CBasePlayer *pl = PlayerFor( id );
	if( !pl )
		return;
	if( add )
	{
		/* svc_addangle: turn by this much and keep whatever the player is looking at on their own */
		pl->pev->avelocity.y += a[1];
		pl->pev->fixangle = 2;
		return;
	}
	pl->pev->angles = pl->pev->v_angle = Vector( a[0], a[1], a[2] );
	pl->pev->fixangle = 1;
}

static void M_Hud( int hide )
{
	g_hud_hide = hide;
	for( int i = 1; i <= gpGlobals->maxClients; i++ )
	{
		CBasePlayer *pl = (CBasePlayer *)UTIL_PlayerByIndex( i );
		if( !pl )
			continue;
		pl->m_iHideHUD &= ~( HIDEHUD_ALL | HIDEHUD_WEAPONS | HIDEHUD_FLASHLIGHT );
		if( hide & DOD_MOHAA_HUD_ALL )
			pl->m_iHideHUD |= HIDEHUD_ALL;
		if( hide & DOD_MOHAA_HUD_WEAPON )
			pl->m_iHideHUD |= HIDEHUD_WEAPONS | HIDEHUD_FLASHLIGHT;
		if( hide & ( DOD_MOHAA_HUD_ALL | DOD_MOHAA_HUD_WEAPON ) )
		{
			if( pl->pev->viewmodel )
			{
				g_saved_viewmodel = pl->pev->viewmodel;
				pl->pev->viewmodel = 0;
			}
		}
		else if( g_saved_viewmodel && !pl->pev->viewmodel )
		{
			pl->pev->viewmodel = g_saved_viewmodel;
			g_saved_viewmodel = 0;
		}
	}
}

/* Send a complete script HUD slot. Index 255 is reserved for a one-packet clear-all. */
static void M_HudDraw( int index, const DodMohaaHudDraw *d )
{
	if( !gmsgMohaaHudDraw )
		return;
	MESSAGE_BEGIN( MSG_ALL, gmsgMohaaHudDraw );
		WRITE_BYTE( index < 0 ? 255 : index );
		if( index >= 0 && d ) {
			WRITE_COORD( d->x ); WRITE_COORD( d->y ); WRITE_COORD( d->w ); WRITE_COORD( d->h );
			WRITE_BYTE( (int)( d->r * 255.0f + 0.5f ) );
			WRITE_BYTE( (int)( d->g * 255.0f + 0.5f ) );
			WRITE_BYTE( (int)( d->b * 255.0f + 0.5f ) );
			WRITE_BYTE( (int)( d->a * 255.0f + 0.5f ) );
			WRITE_BYTE( d->align_x ); WRITE_BYTE( d->align_y ); WRITE_BYTE( d->virtual_size );
			WRITE_STRING( d->text ); WRITE_STRING( d->shader );
		}
	MESSAGE_END();
}

static void M_CompassTarget( const float target[3], int visible )
{
	if( !gmsgMohaaCompass )
		return;
	MESSAGE_BEGIN( MSG_ALL, gmsgMohaaCompass );
		WRITE_BYTE( visible != 0 );
		WRITE_COORD( target ? target[0] : 0.0f );
		WRITE_COORD( target ? target[1] : 0.0f );
		WRITE_COORD( target ? target[2] : 0.0f );
	MESSAGE_END();
}

/* While held, the player cannot fire either (FL_FROZEN only stops movement). */
static void CutsceneThink( void )
{
	CBasePlayer *pl = g_locked_player ? PlayerFor( g_locked_player ) : NULL;
	if( g_locked_player && !pl )
		g_locked_player = 0;
	if( pl )
	{
		pl->m_flNextAttack = UTIL_WeaponTimeBase() + 0.2f;
		pl->pev->button &= ~( IN_ATTACK | IN_ATTACK2 | IN_RELOAD | IN_USE );
	}
	if( g_hud_hide && pl && pl->pev->viewmodel )
	{
		g_saved_viewmodel = pl->pev->viewmodel;	/* a weapon deployed meanwhile stays put away */
		pl->pev->viewmodel = 0;
	}
}

#define MOHAA_DAMAGE_REARM 0.5f

/* A MOHAA damage trigger (the converter gives it spawnflags 2, so no one fires it by touch) whose box holds the point
 * fires as if touched: its targets, its setthread, "waittill trigger". A trigger_once fires only the first time. */
static void M_DamageAt( uint32_t attacker, const float point[3], float radius, float damage )
{
	edict_t *by = attacker ? EdictFor( attacker ) : NULL;
	CBaseEntity *who = by ? CBaseEntity::Instance( by ) : NULL;
	Vector p( point[0], point[1], point[2] );
	if( damage > 0.0f && radius > 0.0f )
		::RadiusDamage( p, who ? who->pev : VARS( INDEXENT( 0 ) ), who ? who->pev : VARS( INDEXENT( 0 ) ), damage, radius,
			CLASS_NONE, DMG_BLAST );
	for( int i = gpGlobals->maxClients + 1; i < gpGlobals->maxEntities; i++ )
	{
		edict_t *e = INDEXENT( i );
		if( !e || e->free || !e->pvPrivateData || !( e->v.spawnflags & 2 ) || !e->v.netname )
			continue;
		const char *cn = STRING( e->v.classname );
		if( strncmp( cn, "trigger_multiple", 16 ) && strncmp( cn, "trigger_once", 12 ) )
			continue;
		if( p.x < e->v.absmin.x - radius || p.y < e->v.absmin.y - radius || p.z < e->v.absmin.z - radius ||
		    p.x > e->v.absmax.x + radius || p.y > e->v.absmax.y + radius || p.z > e->v.absmax.z + radius )
			continue;
		if( e->v.dmgtime > gpGlobals->time )
			continue;
		const int once = !strcmp( cn, "trigger_once" );
		e->v.dmgtime = once ? 1e9f : gpGlobals->time + MOHAA_DAMAGE_REARM;
		CBaseEntity *t = CBaseEntity::Instance( e );
		if( t && !FStringNull( t->pev->target ) )
			t->SUB_UseTargets( who, USE_TOGGLE, 0 );
		DodGC_MohaaTrigger( e, by );
	}
}

static int M_Turret( uint32_t id, int what, uint32_t target, const float v[4] );

static int M_TraceClear( const float a[3], const float b[3], int pass_entities )
{
	TraceResult tr;
	UTIL_TraceLine( Vector( a[0], a[1], a[2] ), Vector( b[0], b[1], b[2] ),
		pass_entities ? ignore_monsters : dont_ignore_monsters, NULL, &tr );
	return !tr.fStartSolid && tr.flFraction >= 1.0f;
}

static int M_Touching( uint32_t a, uint32_t b )
{
	edict_t *ea = EdictFor( a ), *eb = EdictFor( b );
	if( !ea || !eb )
		return 0;
	for( int k = 0; k < 3; k++ )
		if( ea->v.absmin[k] > eb->v.absmax[k] || eb->v.absmin[k] > ea->v.absmax[k] )
			return 0;
	return 1;
}

static void M_DropToFloor( uint32_t id )
{
	edict_t *e = EdictFor( id );
	if( e && !( e->v.flags & FL_CLIENT ) )
		DROP_TO_FLOOR( e );
}

static void M_Shake( float seconds, float magnitude )
{
	/* MOHAA's magnitude runs about 0..2; GoldSrc's shake amplitude is in units, up to 16 */
	float amplitude = magnitude * 4.0f;
	if( amplitude > 16.0f )
		amplitude = 16.0f;
	UTIL_ScreenShakeAll( g_vecZero, amplitude, 10.0f, seconds > 0.0f ? seconds : 1.0f );
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
	/* Renderable script models use a CBaseAnimating point entity; origins remain invisible helpers. */
	if( !strcmp( classname, "script_model" ) || !strcmp( classname, "script_object" ) )
		classname = "mohaa_script_model";
	else if( !strcmp( classname, "script_origin" ) )
		classname = "info_target";
	/* "spawn models/statweapons/x.tik" (a model as the class, as MOHAA allows) or an empty class: no GoldSrc class has
	 * such a name, and asking the engine would only log "No spawn function" */
	if( !classname[0] || strchr( classname, '/' ) || strchr( classname, '.' ) )
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
			continue;	/* script model names are applied by the later .model command, after preloading */
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

#if defined( __GAMECUBE__ )
/* The script VM's memory comes from the engine's map arena tail when it has room: the heap is fragmented by
 * the time a big level has loaded (m1l1 leaves 35 KB free in 11 pieces) while the tail still has megabytes.
 * The arena resets at map change, possibly before the next level init, so the reset hook drops the VM then;
 * hooks run once, so it is registered again on every carve. Heap is the fallback. */
extern "C" size_t GC_MapArenaFind( size_t bytes );
extern "C" void *GC_MapLoadBufferTailAlloc( size_t after_offset, size_t need );
extern "C" void GC_SetMapArenaResetHook( void ( *hook )( void ) );

static void M_PoolReset( void )
{
	Dod_MohaaDropPool();
}

/* One piece of up to want bytes from the arena tail, the largest it has in 32 KB steps (down to 32 KB). */
static void *M_PoolPiece( size_t want, size_t *got )
{
	*got = 0;
	for( size_t bytes = want & ~(size_t)( 32u * 1024u - 1 ); bytes >= 32u * 1024u; bytes -= 32u * 1024u ) {
		size_t at = GC_MapArenaFind( bytes + 32 );
		unsigned char *p;
		if( at == (size_t)-1 )
			continue;
		p = (unsigned char *)GC_MapLoadBufferTailAlloc( at, bytes + 32 );
		if( !p )
			continue;
		*got = bytes;
		return (void *)( ( (unsigned long)p + 31 ) & ~31UL );
	}
	return NULL;
}

/* Script memory from the arena tail: one region when a gap holds it all, else up to 8 pieces, largest first (other
 * residents split the tail: m5l2b had 856 KB free and no 384 KB gap, and later no 192 KB one). The pool spans them. */
static size_t M_PoolCarve( size_t want, DodMohaaBackend *b )
{
	size_t total = 0, got;
	void *p = M_PoolPiece( want, &got );
	if( !p )
		return 0;
	b->pool = p;
	b->pool_size = got;
	total = got;
	for( int r = 0; r < 7 && total + 32u * 1024u <= want; r++ ) {
		p = M_PoolPiece( want - total, &got );
		if( !p )
			break;
		b->pool_more[r] = p;
		b->pool_more_size[r] = got;
		total += got;
	}
	GC_SetMapArenaResetHook( M_PoolReset );
	return total;
}
#endif

/* MOHAA disguise ("$player.has_disguise = 1"): one player in the campaign, so one flag */
static int g_player_disguised;

static void M_Disguise( uint32_t id, int on )
{
	(void)id;
	if( g_player_disguised != !!on )
		ALERT( at_console, "mohaa: player disguise %s\n", on ? "on" : "off" );
	g_player_disguised = !!on;
}

static int M_GetDisguise( uint32_t id )
{
	(void)id;
	return g_player_disguised;
}

int DodGC_MohaaPlayerDisguised( void )
{
	return g_player_disguised;
}

void DodGC_MohaaDisguiseBlown( edict_t *player )
{
	(void)player;
	if( !g_player_disguised )
		return;
	g_player_disguised = 0;
	ALERT( at_console, "mohaa: player fired: disguise blown\n" );
}

void DodGC_MohaaLevelInit( void )
{
	g_probe_goto_done = 0;
	g_probe_fire_from = g_probe_fire_until = 0.0f;
	memset( g_untriggerable, 0, sizeof( g_untriggerable ) );
	DodGC_MohaaRegisterHudMessages();
	if( !g_mohaa_cvar_registered )
	{
		CVAR_REGISTER( &mohaa_script_kb );
		CVAR_REGISTER( &mohaa_probe_goto );
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
	b.set_ammo = M_SetAmmo;
	b.give_item = M_GiveItem;
	b.take_all = M_TakeAll;
	b.use_weapon_class = M_UseWeaponClass;
	b.get_str = M_GetStr;
	b.set_targetname = M_SetTargetname;
	b.set_flag = M_SetFlag;
	b.remove = M_Remove;
	b.set_velocity = M_SetVelocity;
	b.use_targets = M_UseTargets;
	b.spawn = M_Spawn;
	b.sound = M_Sound;
	b.precache_sound = M_Precache;
	b.precache_model = M_PrecacheModel;
	b.set_model = M_SetModel;
	b.set_animation = M_SetAnimation;
	b.actor = M_Actor;
	b.turret = M_Turret;
	b.trace_clear = M_TraceClear;
	b.touching = M_Touching;
	b.shake = M_Shake;
	b.drop_to_floor = M_DropToFloor;
	b.music = M_Music;
	if( g_music_intro[0] )
		M_Music( NULL, NULL );	/* the last map's music stops unless this map starts its own */
	b.walkable = M_Walkable;
	b.get_cvar = M_GetCvar;
	b.fade = M_Fade;
	b.set_cvar = M_SetCvar;
	b.player_lock = M_PlayerLock;
	b.place_player = M_PlacePlayer;
	b.view = M_View;
	b.hud = M_Hud;
	b.hud_draw = M_HudDraw;
	b.compass_target = M_CompassTarget;
	b.damage_at = M_DamageAt;
	b.disguise = M_Disguise;
	b.get_disguise = M_GetDisguise;
	g_locked_player = 0;	/* a new map starts everyone free (the last map's VM let go in its shutdown) */
	g_player_disguised = 0;
	g_saved_viewmodel = 0;
	g_hud_hide = 0;
	g_nwaiting = 0;	/* the last map's waiting soldiers went with it */
	g_mohaa_script_model_count = 0;
	memset( g_mohaa_script_models, 0, sizeof( g_mohaa_script_models ) );
	memset( g_actors, 0, sizeof( g_actors ) );
	memset( g_dead, 0, sizeof( g_dead ) );
	g_next_waiting_check = 0.0f;
	size_t budget = (size_t)CVAR_GET_FLOAT( "mohaa_script_kb" ) * 1024u;
	size_t arena = 0;	/* bytes of the budget in the map arena; the rest comes from the heap when needed */
#if defined( __GAMECUBE__ )
	{
		char scr[96];
		snprintf( scr, sizeof( scr ), "maps/%s.scr", STRING( gpGlobals->mapname ) );
		/* only a level with a script spends arena on it */
		if( budget && g_engfuncs.pfnGetFileSize && g_engfuncs.pfnGetFileSize( scr ) > 0 ) {
			arena = M_PoolCarve( budget, &b );
			if( !arena )
				ALERT( at_console, "mohaa: no gap of 32 KiB or more in the map arena for script memory, using the heap\n" );
		}
	}
#endif
	if( Dod_MohaaLevelInit( &b, STRING( gpGlobals->mapname ), gpGlobals->time, budget ) ) {
		DodGrunts_PrecacheBodies();	/* the mission's soldiers wear the sides' player bodies */
		int pieces = b.pool ? 1 : 0;
		for( int r = 0; r < 7; r++ )
			pieces += b.pool_more[r] != NULL;
		ALERT( at_console, "mohaa: running maps/%s.scr (budget %u KiB, %u KiB in the map arena in %d piece%s, the rest from the heap)\n",
			STRING( gpGlobals->mapname ), (unsigned)( budget / 1024u ), (unsigned)( arena / 1024u ), pieces, pieces == 1 ? "" : "s" );
	}
}

/* MOHAA's "press USE here" triggers (the m1l2a locked gate's door_locked, mission objectives) are trigger_use brushes,
 * which mohaa-gc's converter writes as trigger_use or trigger_multiple. Stock GoldSrc USE only reaches entities with
 * FCAP_IMPULSE_USE, so a real controller press never fired them. The nearest one within reach of the player, measured
 * to the nearest point of the brush (door triggers are long and thin), takes the press. */
#define MOHAA_USE_REACH 128.0f

static float MohaaUseDistance( CBaseEntity *ent, const Vector &at )
{
	Vector closest;
	for( int axis = 0; axis < 3; axis++ )
	{
		float v = at[axis];
		if( v < ent->pev->absmin[axis] ) v = ent->pev->absmin[axis];
		if( v > ent->pev->absmax[axis] ) v = ent->pev->absmax[axis];
		closest[axis] = v;
	}
	return ( closest - at ).Length();
}

static int RiderUse( CBasePlayer *pl );

int DodGC_MohaaPlayerUse( CBasePlayer *player )
{
	static const char *const classes[] = { "trigger_use", "trigger_multiple" };
	CBaseEntity *best = NULL;
	float best_dist = MOHAA_USE_REACH;
	const char *gamedir = CVAR_GET_STRING( "gamedir" );
	if( !player || !gamedir || strcmp( gamedir, "mohaa" ) || !( player->m_afButtonPressed & IN_USE ) )
		return 0;
	/* a soldier asking a disguised player for papers: USE shows them (retail's "toggleitem" key has no pad button) */
	if( Dod_MohaaShowPapers( IdFor( player->edict() ) ) )
		return 1;
	if( RiderUse( player ) )
		return 1;
	for( int k = 0; k < 2; k++ )
	{
		edict_t *e = NULL;
		while( !FNullEnt( e = FIND_ENTITY_BY_CLASSNAME( e, classes[k] ) ) )
		{
			CBaseEntity *ent = CBaseEntity::Instance( e );
			if( !ent || Untriggerable( e ) )
				continue;
			const float d = MohaaUseDistance( ent, player->pev->origin + player->pev->view_ofs * 0.5f );
			if( d < best_dist )
			{
				best = ent;
				best_dist = d;
			}
		}
	}
	if( !best )
		return 0;
	ALERT( at_console, "mohaa: USE %s %s at %.0f units\n", STRING( best->pev->classname ),
		best->pev->targetname ? STRING( best->pev->targetname ) : "", best_dist );
	if( FClassnameIs( best->pev, "trigger_use" ) )
		best->Use( player, player, USE_TOGGLE, 0 );
	else
		best->Touch( player );
	return 1;
}

void DodGC_MohaaActorAlerted( edict_t *e )
{
	const uint32_t id = IdFor( e );
	if( id )
		Dod_MohaaActorAlerted( id );
}

void DodGC_MohaaPrecacheModels( void )
{
	Dod_MohaaPrecacheModels();
}

void DodGC_MohaaTrigger( edict_t *e, edict_t *activator )
{
	Dod_MohaaSetOther( IdFor( activator ) );
	DodGC_MohaaEntityEvent( e, "trigger" );
}

/* MOHAA turretweapons. The map converter writes them as info_target with mohaa_classname turretweapon_*; the MG
 * ones get crews: an actor whose map target names the gun, or one told type_attack "turret" beside it. */
#define MOHAA_TURRETS 16
#define MOHAA_MG42_MODEL "models/statweapons/mg42_gun.mdl"
static struct {
	uint32_t id;
	float arc;
	unsigned char mg, modelled;
	unsigned char firing;	/* startfiring: the gun fires at its aim target in bursts */
	unsigned char burst_on;
	uint32_t crew;		/* the soldier on the gun, 0 none */
	uint32_t aim;		/* setaimtarget, 0 none */
	float base_yaw;		/* the map's yaw: the arc's centre */
	float burst[4];		/* burstfiresettings: on min, on max, off min, off max (seconds) */
	float burst_until, next_shot;
} g_turrets[MOHAA_TURRETS];
static int g_nturrets;
/* map actors waiting for their gun to spawn (keys arrive before the turret entities do) */
#define MOHAA_CREWS 16
static struct { uint32_t actor; string_t gun; float actor_added_at; } g_crews[MOHAA_CREWS];
static int g_ncrews;

static void TurretsReset( void );
static string_t g_turrets_map;

static int TurretRow( edict_t *e, int make )
{
	const uint32_t id = IdFor( e );
	/* the rows belong to one map: the first key of a new map clears them (map keys arrive before any level hook) */
	if( make && g_turrets_map != gpGlobals->mapname ) {
		TurretsReset();
		g_turrets_map = gpGlobals->mapname;
	}
	for( int k = 0; k < g_nturrets; k++ )
		if( g_turrets[k].id == id )
			return k;
	if( !make || g_nturrets >= MOHAA_TURRETS )
		return -1;
	g_turrets[g_nturrets].id = id;
	g_turrets[g_nturrets].arc = 0.0f;
	g_turrets[g_nturrets].mg = 0;
	g_turrets[g_nturrets].modelled = 0;
	g_turrets[g_nturrets].firing = g_turrets[g_nturrets].burst_on = 0;
	g_turrets[g_nturrets].crew = g_turrets[g_nturrets].aim = 0;
	g_turrets[g_nturrets].base_yaw = 0.0f;
	g_turrets[g_nturrets].burst[0] = 0.5f; g_turrets[g_nturrets].burst[1] = 1.5f;	/* retail-like defaults */
	g_turrets[g_nturrets].burst[2] = 0.5f; g_turrets[g_nturrets].burst[3] = 1.0f;
	g_turrets[g_nturrets].burst_until = g_turrets[g_nturrets].next_shot = 0.0f;
	return g_nturrets++;
}

static void TurretsReset( void )
{
	g_nturrets = 0;
	g_ncrews = 0;
}

int DodGC_MohaaTurretNear( const float from[3], float radius, float gun[4], edict_t *crew )
{
	int best = -1;
	float best_d2 = radius * radius;
	for( int k = 0; k < g_nturrets; k++ ) {
		edict_t *t = g_turrets[k].mg ? EdictFor( g_turrets[k].id ) : NULL;
		if( !t )
			continue;
		const float dx = t->v.origin.x - from[0], dy = t->v.origin.y - from[1];
		if( dx * dx + dy * dy < best_d2 ) {
			best_d2 = dx * dx + dy * dy;
			best = k;
		}
	}
	if( best < 0 )
		return 0;
	edict_t *t = EdictFor( g_turrets[best].id );
	gun[0] = t->v.origin.x;
	gun[1] = t->v.origin.y;
	gun[2] = t->v.angles.y;
	gun[3] = g_turrets[best].arc;
	if( crew )
		g_turrets[best].crew = IdFor( crew );
	return 1;
}

static void CrewWait( edict_t *actor, string_t gun )
{
	if( g_turrets_map != gpGlobals->mapname ) {
		TurretsReset();
		g_turrets_map = gpGlobals->mapname;
	}
	if( !actor || !gun || g_ncrews >= MOHAA_CREWS )
		return;
	g_crews[g_ncrews].actor = IdFor( actor );
	g_crews[g_ncrews].gun = gun;
	g_crews[g_ncrews].actor_added_at = gpGlobals->time;
	g_ncrews++;
}

static int ScriptModelPrecached( const char *path );

static void ProbeGotoThink( void )
{
	char file_name[64] = "";
	const char *name = CVAR_GET_STRING( "mohaa_probe_goto" );
	if( g_probe_goto_done || gpGlobals->time < 2.0f )
		return;
	g_probe_goto_done = 1;
	if( !name || !name[0] ) {
		char path[96];
		int len = 0;
		snprintf( path, sizeof( path ), "maps/%s.goto", STRING( gpGlobals->mapname ) );
		byte *data = LOAD_FILE_FOR_ME( path, &len );
		if( !data )
			return;
		int n = 0;
		while( n < len && n + 1 < (int)sizeof( file_name ) && data[n] != '\n' && data[n] != '\r' ) {
			file_name[n] = (char)data[n];
			n++;
		}
		file_name[n] = 0;
		FREE_FILE( data );
		name = file_name;
		if( !name[0] )
			return;
	}
	/* "<name> [behind] [free]": behind stands the player at the back of the entity (a turret's gunner spot);
	 * free takes a turret's crew off it, so the player can man it */
	char target[64];
	const int behind = strstr( name, " behind" ) != NULL;
	const int free_gun = strstr( name, " free" ) != NULL;
	/* "mount": then press USE for the player; "fire": then hold the gun's trigger for 8 s, sweeping the view
	 * across the arc (a probe stand-in for the pad, whose TAS polls don't keep time with the map) */
	const int mount = strstr( name, " mount" ) != NULL;
	const int fire = strstr( name, " fire" ) != NULL;
	snprintf( target, sizeof( target ), "%s", name );
	if( strchr( target, ' ' ) )
		*strchr( target, ' ' ) = 0;
	edict_t *spot = FIND_ENTITY_BY_TARGETNAME( NULL, target );
	edict_t *pe = INDEXENT( 1 );
	if( FNullEnt( spot ) || !pe || pe->free ) {
		ALERT( at_console, "mohaa_probe_goto: no %s\n", target );
		return;
	}
	if( free_gun ) {
		const int k = TurretRow( spot, 0 );
		edict_t *crew = k >= 0 && g_turrets[k].crew ? EdictFor( g_turrets[k].crew ) : NULL;
		if( crew ) {
			ALERT( at_console, "mohaa_probe_goto: %s's crew leaves the gun\n", target );
			DodGrunts_ScriptRemove( crew );
			g_turrets[k].crew = 0;
		}
	}
	const int near_it = strstr( name, " near" ) != NULL;
	float r = spot->v.angles.y * 0.017453293f;
	if( near_it ) {
		/* "near": 150 units from it (a soldier's disguise_range is 256), on the side the player comes from, so the
		 * spot is in the open rather than through the wall behind a soldier facing it */
		const Vector away = pe->v.origin - spot->v.origin;
		r = atan2f( away.y, away.x );
	}
	const float d = behind ? -40.0f : ( near_it ? 150.0f : 700.0f );
	Vector to = spot->v.origin + Vector( cosf( r ) * d, sinf( r ) * d, 48.0f );
	TraceResult tr;
	if( near_it ) {
		/* walk out from the soldier's own (open) spot, stopping short of any wall */
		const Vector from = spot->v.origin + Vector( 0, 0, 40.0f );
		UTIL_TraceHull( from, from + Vector( cosf( r ) * d, sinf( r ) * d, 0 ), ignore_monsters, human_hull, pe, &tr );
		if( !tr.fStartSolid )
			to = tr.vecEndPos;
	}
	UTIL_TraceHull( to, to - Vector( 0, 0, 512 ), ignore_monsters, human_hull, pe, &tr );
	if( !tr.fStartSolid )
		to = tr.vecEndPos;
	UTIL_SetOrigin( &pe->v, to );
	const Vector look = behind ? Vector( 0, spot->v.angles.y, 0 ) : UTIL_VecToAngles( spot->v.origin - to );
	pe->v.angles = Vector( -look.x, look.y, 0 );	/* fixangle sends these as the view: look up (or down) at it */
	pe->v.v_angle = pe->v.angles;
	pe->v.fixangle = 1;
	ALERT( at_console, "mohaa_probe_goto: player at %.0f %.0f %.0f %s %s\n", to.x, to.y, to.z,
		behind ? "behind" : "facing", target );
	if( mount ) {
		CBaseEntity *ent = CBaseEntity::Instance( pe );
		if( ent && ent->IsPlayer() && RiderUse( (CBasePlayer *)ent ) && fire ) {
			g_probe_fire_from = gpGlobals->time + 2.0f;
			g_probe_fire_until = g_probe_fire_from + 8.0f;
		}
	}
}

static float WrapYaw( float a )
{
	while( a > 180.0f ) a -= 360.0f;
	while( a < -180.0f ) a += 360.0f;
	return a;
}

static float RandIn( float lo, float hi )
{
	return hi > lo ? RANDOM_FLOAT( lo, hi ) : lo;
}

/* The gun turns with its aim: toward its setaimtarget, else the way its crew faces, inside the arc either side of the
 * map's yaw. With startfiring and an aim target it fires on its own in bursts (burstfiresettings): the MG42's retail
 * sound each shot, and a hit on a player in plain sight now and then. */
static void TurretAimAndFire( int k )
{
	edict_t *t = g_turrets[k].mg && g_turrets[k].modelled ? EdictFor( g_turrets[k].id ) : NULL;
	if( !t )
		return;
	edict_t *aim = g_turrets[k].aim ? EdictFor( g_turrets[k].aim ) : NULL;
	edict_t *crew = g_turrets[k].crew ? EdictFor( g_turrets[k].crew ) : NULL;
	if( crew && crew->v.health <= 0 )
		crew = NULL;
	float want = g_turrets[k].base_yaw;
	if( aim )
		want = UTIL_VecToAngles( aim->v.origin - t->v.origin ).y;
	else if( crew )
		want = crew->v.angles.y;
	const float arc = g_turrets[k].arc > 0.0f ? g_turrets[k].arc : DOD_GRUNT_TURRET_ARC;
	float off = WrapYaw( want - g_turrets[k].base_yaw );
	if( off > arc ) off = arc;
	if( off < -arc ) off = -arc;
	t->v.angles.y = g_turrets[k].base_yaw + off;
	if( !g_turrets[k].firing || !aim )
		return;
	const float now = gpGlobals->time;
	if( now >= g_turrets[k].burst_until ) {
		g_turrets[k].burst_on = !g_turrets[k].burst_on;
		g_turrets[k].burst_until = now + ( g_turrets[k].burst_on ? RandIn( g_turrets[k].burst[0], g_turrets[k].burst[1] )
			: RandIn( g_turrets[k].burst[2], g_turrets[k].burst[3] ) );
	}
	if( !g_turrets[k].burst_on || now < g_turrets[k].next_shot )
		return;
	g_turrets[k].next_shot = now + 0.12f;	/* the MG42's 0.06 s fire delay, every other round */
	if( !Dod_MohaaEntitySound( g_turrets[k].id, "mg42_gun_snd_fire" ) )
		;	/* no retail alias staged: silent, as before */
	if( !( aim->v.flags & FL_CLIENT ) || aim->v.health <= 0 || RANDOM_FLOAT( 0.0f, 1.0f ) > 0.15f )
		return;
	TraceResult tr;
	const Vector from = t->v.origin + Vector( 0, 0, 8 );
	UTIL_TraceLine( from, aim->v.origin + aim->v.view_ofs * 0.5f, dont_ignore_monsters, t, &tr );
	if( tr.pHit != aim )
		return;
	CBaseEntity *victim = CBaseEntity::Instance( aim );
	if( victim ) {
		ClearMultiDamage();
		victim->TraceAttack( VARS( t ), 8.0f, ( aim->v.origin - from ).Normalize(), &tr, DMG_BULLET | DMG_NEVERGIB );
		ApplyMultiDamage( VARS( t ), VARS( t ) );
	}
}

/* The player on an MG42 (USE behind a gun with no crew): held in place like a scripted ride, the gun turns with their
 * view inside its arc, the attack button fires it, USE again (or dying) lets go. */
static uint32_t g_rider;
static int g_rider_turret = -1;
static int g_rider_movetype;
static string_t g_rider_viewmodel;
static float g_rider_next_shot;

static void RiderRelease( void )
{
	CBasePlayer *pl = g_rider ? PlayerFor( g_rider ) : NULL;
	if( pl ) {
		pl->pev->movetype = g_rider_movetype ? g_rider_movetype : MOVETYPE_WALK;
		pl->pev->flags &= ~FL_FROZEN;
		if( g_rider_viewmodel && !pl->pev->viewmodel )
			pl->pev->viewmodel = g_rider_viewmodel;
		ALERT( at_console, "mohaa: the player leaves the MG42\n" );
	}
	g_rider = 0;
	g_rider_turret = -1;
	g_rider_viewmodel = 0;
}

/* USE: get off the gun, or on one within reach whose crew is gone. 1 when the press was used. */
static int RiderUse( CBasePlayer *pl )
{
	if( g_rider ) {
		RiderRelease();
		return 1;
	}
	if( g_turrets_map != gpGlobals->mapname )
		return 0;
	int best = -1;
	float best_d = 80.0f;
	for( int k = 0; k < g_nturrets; k++ ) {
		edict_t *t = g_turrets[k].mg ? EdictFor( g_turrets[k].id ) : NULL;
		edict_t *crew = g_turrets[k].crew ? EdictFor( g_turrets[k].crew ) : NULL;
		if( !t || ( crew && crew->v.health > 0 ) )
			continue;
		const float d = ( t->v.origin - pl->pev->origin ).Length2D();
		if( d < best_d ) {
			best = k;
			best_d = d;
		}
	}
	if( best < 0 )
		return 0;
	edict_t *t = EdictFor( g_turrets[best].id );
	g_rider = IdFor( pl->edict() );
	g_rider_turret = best;
	g_rider_movetype = pl->pev->movetype;
	g_rider_viewmodel = pl->pev->viewmodel;
	pl->pev->viewmodel = 0;
	pl->pev->movetype = MOVETYPE_NOCLIP;
	pl->pev->flags |= FL_FROZEN;
	pl->pev->velocity = g_vecZero;
	/* eyes just over the gun, a little behind it */
	const float r = g_turrets[best].base_yaw * 0.017453293f;
	const Vector eye = t->v.origin + Vector( -cosf( r ) * 40.0f, -sinf( r ) * 40.0f, 14.0f );
	UTIL_SetOrigin( pl->pev, eye - pl->pev->view_ofs );
	ALERT( at_console, "mohaa: the player mans the MG42 %s\n", t->v.targetname ? STRING( t->v.targetname ) : "" );
	return 1;
}

static void RiderThink( void )
{
	CBasePlayer *pl = g_rider ? PlayerFor( g_rider ) : NULL;
	if( !g_rider )
		return;
	edict_t *t = g_rider_turret >= 0 ? EdictFor( g_turrets[g_rider_turret].id ) : NULL;
	if( !pl || !t || pl->pev->health <= 0 || g_turrets_map != gpGlobals->mapname ) {
		RiderRelease();
		return;
	}
	pl->pev->velocity = g_vecZero;
	const int k = g_rider_turret;
	const float arc = g_turrets[k].arc > 0.0f ? g_turrets[k].arc : DOD_GRUNT_TURRET_ARC;
	float off = WrapYaw( pl->pev->v_angle.y - g_turrets[k].base_yaw );
	if( off > arc ) off = arc;
	if( off < -arc ) off = -arc;
	t->v.angles.y = g_turrets[k].base_yaw + off;
	float pitch = pl->pev->v_angle.x;
	if( pitch > 25.0f ) pitch = 25.0f;
	if( pitch < -25.0f ) pitch = -25.0f;
	t->v.angles.x = -pitch;
	int firing = ( pl->pev->button & IN_ATTACK ) != 0;
	if( gpGlobals->time >= g_probe_fire_from && gpGlobals->time < g_probe_fire_until ) {
		/* probe aid: trigger held, the view sweeping across the arc and back */
		const float u = ( gpGlobals->time - g_probe_fire_from ) / ( g_probe_fire_until - g_probe_fire_from );
		const float sweep = sinf( u * 6.2831853f ) * ( arc * 0.8f );
		pl->pev->angles = Vector( 10.0f, g_turrets[k].base_yaw + sweep, 0 );
		pl->pev->v_angle = pl->pev->angles;
		pl->pev->fixangle = 1;
		firing = 1;
		off = sweep;
		t->v.angles.y = g_turrets[k].base_yaw + off;
	}
	/* the player's own gun stays quiet while they are on the MG */
	pl->m_flNextAttack = UTIL_WeaponTimeBase() + 0.2f;
	pl->pev->button &= ~( IN_ATTACK | IN_ATTACK2 );
	if( !firing || gpGlobals->time < g_rider_next_shot )
		return;
	if( gpGlobals->time >= g_probe_fire_until - 0.05f && gpGlobals->time < g_probe_fire_until + 0.2f )
		ALERT( at_console, "mohaa: the player's MG42 burst ends\n" );
	g_rider_next_shot = gpGlobals->time + 0.1f;
	Dod_MohaaEntitySound( g_turrets[k].id, "mg42_gun_snd_fire" );
	UTIL_MakeVectors( Vector( pitch, t->v.angles.y, 0 ) );
	const Vector from = pl->pev->origin + pl->pev->view_ofs;
	TraceResult tr;
	UTIL_TraceLine( from, from + gpGlobals->v_forward * 4096.0f, dont_ignore_monsters, pl->edict(), &tr );
	CBaseEntity *hit = tr.pHit ? CBaseEntity::Instance( tr.pHit ) : NULL;
	if( hit && hit->pev->takedamage != DAMAGE_NO && hit != pl ) {
		ClearMultiDamage();
		hit->TraceAttack( pl->pev, 40.0f, gpGlobals->v_forward, &tr, DMG_BULLET | DMG_NEVERGIB );
		ApplyMultiDamage( pl->pev, pl->pev );
	}
}

/* Once the map's entities are in: each MG gets its model, each waiting crew mans its gun. */
static void TurretsThink( void )
{
	static string_t logged_map;
	ProbeGotoThink();
	if( logged_map != gpGlobals->mapname ) {
		logged_map = gpGlobals->mapname;
		ALERT( at_console, "mohaa: %d turretweapons, %d crews waiting\n", g_turrets_map == gpGlobals->mapname ? g_nturrets : 0,
			g_turrets_map == gpGlobals->mapname ? g_ncrews : 0 );
	}
	if( g_turrets_map != gpGlobals->mapname )
		return;	/* rows of an earlier map */
	for( int k = 0; k < g_nturrets; k++ ) {
		edict_t *t = EdictFor( g_turrets[k].id );
		if( !t || !g_turrets[k].mg || g_turrets[k].modelled )
			continue;
		g_turrets[k].modelled = 1;
		g_turrets[k].base_yaw = t->v.angles.y;
		if( ScriptModelPrecached( MOHAA_MG42_MODEL ) ) {
			SET_MODEL( t, MOHAA_MG42_MODEL );
			t->v.solid = SOLID_NOT;
			t->v.movetype = MOVETYPE_NONE;
			t->v.effects &= ~EF_NODRAW;
		}
	}
	for( int c = 0; c < g_ncrews; ) {
		edict_t *actor = EdictFor( g_crews[c].actor );
		int done = !actor;
		if( !actor )
			ALERT( at_console, "mohaa: the crew of %s is gone before it reached the gun\n", STRING( g_crews[c].gun ) );
		for( int k = 0; !done && k < g_nturrets; k++ ) {
			edict_t *t = g_turrets[k].mg ? EdictFor( g_turrets[k].id ) : NULL;
			if( t && t->v.targetname && !strcmp( STRING( t->v.targetname ), STRING( g_crews[c].gun ) ) ) {
				if( !DodGrunts_ManTurret( actor, t->v.angles.y, g_turrets[k].arc ) )
					ALERT( at_console, "mohaa: %s cannot man the MG42 %s (not a script soldier)\n",
						actor->v.targetname ? STRING( actor->v.targetname ) : "actor", STRING( g_crews[c].gun ) );
				else if( ( g_turrets[k].crew = IdFor( actor ) ) )
					ALERT( at_console, "mohaa: %s mans the MG42 %s\n",
						actor->v.targetname ? STRING( actor->v.targetname ) : "actor", STRING( g_crews[c].gun ) );
				done = 1;
			}
		}
		if( !done && gpGlobals->time > 10.0f && g_crews[c].actor_added_at + 10.0f < gpGlobals->time )
			ALERT( at_console, "mohaa: no turretweapon %s for its crew\n", STRING( g_crews[c].gun ) );
		if( done || g_crews[c].actor_added_at + 10.0f < gpGlobals->time ) {
			g_crews[c] = g_crews[--g_ncrews];
			continue;
		}
		c++;
	}
	for( int k = 0; k < g_nturrets; k++ )
		if( !g_rider || k != g_rider_turret )
			TurretAimAndFire( k );
	RiderThink();
}

static int M_Turret( uint32_t id, int what, uint32_t target, const float v[4] )
{
	edict_t *e = EdictFor( id );
	const int k = e && g_turrets_map == gpGlobals->mapname ? TurretRow( e, 0 ) : -1;
	if( k < 0 )
		return 0;
	switch( what ) {
	case DOD_MOHAA_TURRET_AIM: g_turrets[k].aim = target; break;
	case DOD_MOHAA_TURRET_START: g_turrets[k].firing = 1; break;
	case DOD_MOHAA_TURRET_STOP: g_turrets[k].firing = 0; g_turrets[k].burst_on = 0; break;
	case DOD_MOHAA_TURRET_BURST:
		for( int i = 0; i < 4; i++ )
			g_turrets[k].burst[i] = v && v[i] > 0.0f ? v[i] : g_turrets[k].burst[i];
		break;
	case DOD_MOHAA_TURRET_YAWCAP: if( v && v[0] > 0.0f ) g_turrets[k].arc = v[0]; break;
	default: break;
	}
	return 1;
}

uint32_t DodGC_MohaaEntityId( edict_t *e )
{
	return IdFor( e );
}

void DodGC_MohaaEntityKey( edict_t *e, const char *key, const char *value )
{
	/* mohaa_classname is the converter's note of the retail class: only turretweapons are kept, never sent to the
	 * script (every converted entity has one) */
	if( !strcmp( key, "mohaa_classname" ) ) {
		if( !strncmp( value, "turretweapon_", 13 ) ) {
			const int k = TurretRow( e, 1 );
			if( k >= 0 )
				g_turrets[k].mg = strstr( value, "mg42" ) || strstr( value, "30cal" ) ? 1 : 0;
		}
		return;
	}
	if( !strcmp( key, "#maxyawoffset" ) ) {
		const int k = TurretRow( e, 1 );
		if( k >= 0 )
			g_turrets[k].arc = (float)atof( value );
	}
	uint32_t id = IdFor( e );
	if( id )
		Dod_MohaaEntityKey( id, key, value );
}

void DodGC_MohaaThink( void )
{
	Dod_MohaaThink( gpGlobals->time );
	CutsceneThink();
	MusicSend();
	ActorsWaitingThink();
	TurretsThink();
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
