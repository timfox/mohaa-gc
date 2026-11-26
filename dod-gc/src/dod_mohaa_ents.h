#ifndef DODGC_DOD_MOHAA_ENTS_H
#define DODGC_DOD_MOHAA_ENTS_H

/* Game-DLL entry points of the MOHAA script binding (dod_mohaa_ents.cpp). */

/* At map start (game rules construction): runs maps/<map>.scr if the map has one. */
void DodGC_MohaaLevelInit( void );
void DodGC_MohaaRegisterHudMessages( void );
/* Every game rules Think. */
void DodGC_MohaaThink( void );
/* An entity event a script can wait for, e.g. ("trigger") from a trigger firing. */
void DodGC_MohaaEntityEvent( edict_t *e, const char *event );

/* A trigger fired, set off by activator (may be NULL): the script sees the activator as parm.other. */
void DodGC_MohaaTrigger( edict_t *e, edict_t *activator );
/* DispatchKeyValue: a key starting with '#' (MOHAA "#set", "#group") is for scripts only. */
void DodGC_MohaaEntityKey( edict_t *e, const char *key, const char *value );

/* CBasePlayer::PlayerUse, on a fresh USE press: a MOHAA trigger_use (Use) or trigger_multiple (Touch) brush within
 * reach of the player fires. 1 when one did, so the stock door/button search is skipped this press. */
class CBasePlayer;
int DodGC_MohaaPlayerUse( CBasePlayer *player );

#endif
