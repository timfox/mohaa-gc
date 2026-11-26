/* Day of Defeat HUD (client); see hud_dod.h, dod_hud.h and dod_hud_retail.h. */
#include "hud.h"
#include "cl_util.h"
#include "parsemsg.h"
#include "ammohistory.h"

#include <math.h>

int __MsgFunc_DodHud( const char *pszName, int iSize, void *pbuf )
{
	return gHUD.m_Dod.MsgFunc_DodHud( pszName, iSize, pbuf );
}

int __MsgFunc_DodKill( const char *pszName, int iSize, void *pbuf )
{
	return gHUD.m_Dod.MsgFunc_DodKill( pszName, iSize, pbuf );
}

int __MsgFunc_DodVoice( const char *pszName, int iSize, void *pbuf )
{
	return gHUD.m_Dod.MsgFunc_DodVoice( pszName, iSize, pbuf );
}

int __MsgFunc_DodBoard( const char *pszName, int iSize, void *pbuf )
{
	return gHUD.m_Dod.MsgFunc_DodBoard( pszName, iSize, pbuf );
}

int __MsgFunc_MohaaHudDraw( const char *pszName, int iSize, void *pbuf )
{
	return gHUD.m_Dod.MsgFunc_MohaaHudDraw( pszName, iSize, pbuf );
}

int __MsgFunc_MohaaCompass( const char *pszName, int iSize, void *pbuf )
{
	return gHUD.m_Dod.MsgFunc_MohaaCompass( pszName, iSize, pbuf );
}

void CHudDod::InitState( void )
{
	int i;

	if( m_pCvar )
		return;	/* Init after InitState: already registered */
	memset( &m_state, 0, sizeof( m_state ) );
	memset( m_mohaaHud, 0, sizeof( m_mohaaHud ) );
	memset( m_hMohaaHudShader, 0, sizeof( m_hMohaaHudShader ) );
	memset( m_mohaaHudShaderTried, 0, sizeof( m_mohaaHudShaderTried ) );
	memset( m_mohaaCompassTarget, 0, sizeof( m_mohaaCompassTarget ) );
	m_mohaaCompassHasTarget = 0;
	m_mohaaCompassTried = 0;
	m_flMohaaHintUntil = 0.0f;
	m_hMohaaCompassBack = m_hMohaaCompassFace = m_hMohaaCompassNeedle = m_hMohaaCompassObjective = 0;
	memset( m_szMohaaHudShader, 0, sizeof( m_szMohaaHudShader ) );
	m_flLastUpdate = 0.0f;
	m_flTimerBase = 0.0f;
	m_fHaveState = 0;
	for( i = 0; i < DOD_SHEET_COUNT; i++ )
		m_hSheets[i] = 0;
	m_fSheetsTried = 0;
	m_fSheetTried = 0;
	m_fDrawLogged = 0;
	m_szLoggedWeapon[0] = 0;
	/* A `set cl_dodhud 0` from a config that ran before the HUD came up must survive: reuse the cvar when it exists. */
	m_pCvar = gEngfuncs.pfnGetCvarPointer( "cl_dodhud" );
	if( !m_pCvar )
	{
		/* MOHAA shares this client DLL but must use its own HUD path. Default
		 * the DoD retail overlay on only for the DoD game directory; an explicit
		 * cl_dodhud value in a user config still takes precedence above. */
		const char *default_value = HUD_IsGame( "dod" ) ? "1" : "0";
		m_pCvar = gEngfuncs.pfnRegisterVariable( "cl_dodhud", default_value, FCVAR_ARCHIVE );
	}
	/* The engine's lean/probe route (CapFaces, vid_gamecube.c) paints its own TEAM / HP / AMMO bars; it checks this flag so it
	 * does not draw a second ammo readout over the retail one. */
	if( !gEngfuncs.pfnGetCvarPointer( "gc_hud_retail" ))
		gEngfuncs.pfnRegisterVariable( "gc_hud_retail", "0", 0 );
	HOOK_MESSAGE( DodHud );
	HOOK_MESSAGE( DodBoard );
	HOOK_MESSAGE( DodVoice );
	HOOK_MESSAGE( DodKill );
	HOOK_MESSAGE( MohaaHudDraw );
	HOOK_MESSAGE( MohaaCompass );
	m_nKills = 0;
	m_fChatting = 0;
	m_szVoice[0] = 0;
	m_iVoiceSel = 0;
	m_flVoiceTime = 0.0f;
	m_fVoiceShown = 0;
	m_szBoard[0] = 0;
	m_flBoardTime = 0.0f;
	m_fBoardShown = 0;
}

int CHudDod::Init( void )
{
	InitState();
	m_iFlags = HUD_ACTIVE;
	gHUD.AddHudElem( this );
	return 1;
}

int CHudDod::VidInit( void )
{
	int i;

	/* Sprite handles do not survive a video restart: load again on demand. */
	for( i = 0; i < DOD_SHEET_COUNT; i++ )
		m_hSheets[i] = 0;
	m_fSheetsTried = 0;
	m_fSheetTried = 0;
	m_mohaaCompassTried = 0;
	m_hMohaaCompassBack = m_hMohaaCompassFace = m_hMohaaCompassNeedle = m_hMohaaCompassObjective = 0;
	memset( m_hMohaaHudShader, 0, sizeof( m_hMohaaHudShader ) );
	memset( m_mohaaHudShaderTried, 0, sizeof( m_mohaaHudShaderTried ) );
	return 1;
}

int CHudDod::MsgFunc_MohaaHudDraw( const char *pszName, int iSize, void *pbuf )
{
	DodMohaaHudDraw *d;
	int index;
	const char *text, *shader;
	(void)pszName;
	BEGIN_READ( pbuf, iSize );
	index = READ_BYTE();
	if( index == 255 ) {
		memset( m_mohaaHud, 0, sizeof( m_mohaaHud ) );
		memset( m_mohaaHudShaderTried, 0, sizeof( m_mohaaHudShaderTried ) );
		memset( m_szMohaaHudShader, 0, sizeof( m_szMohaaHudShader ) );
		return 1;
	}
	if( index < 0 || index >= DOD_MOHAA_HUD_DRAW_COUNT )
		return 1;
	d = &m_mohaaHud[index];
	d->x = READ_COORD(); d->y = READ_COORD(); d->w = READ_COORD(); d->h = READ_COORD();
	d->r = READ_BYTE() / 255.0f; d->g = READ_BYTE() / 255.0f;
	d->b = READ_BYTE() / 255.0f; d->a = READ_BYTE() / 255.0f;
	d->align_x = READ_BYTE(); d->align_y = READ_BYTE(); d->virtual_size = READ_BYTE();
	text = READ_STRING();
	strncpy( d->text, text ? text : "", sizeof( d->text ) - 1 );
	d->text[sizeof( d->text ) - 1] = 0;
	shader = READ_STRING();
	strncpy( d->shader, shader ? shader : "", sizeof( d->shader ) - 1 );
	d->shader[sizeof( d->shader ) - 1] = 0;
	if( index == DOD_MOHAA_HUD_HINT_INDEX )
		m_flMohaaHintUntil = d->text[0] && d->a > 0.0f ? gHUD.m_flTime + 5.0f : 0.0f;
	if( strcmp( m_szMohaaHudShader[index], d->shader )) {
		strncpy( m_szMohaaHudShader[index], d->shader, sizeof( m_szMohaaHudShader[index] ) - 1 );
		m_szMohaaHudShader[index][sizeof( m_szMohaaHudShader[index] ) - 1] = 0;
		m_mohaaHudShaderTried[index] = 0;
		m_hMohaaHudShader[index] = 0;
	}
	return 1;
}

int CHudDod::MsgFunc_MohaaCompass( const char *pszName, int iSize, void *pbuf )
{
	(void)pszName;
	BEGIN_READ( pbuf, iSize );
	m_mohaaCompassHasTarget = READ_BYTE() != 0;
	m_mohaaCompassTarget[0] = READ_COORD();
	m_mohaaCompassTarget[1] = READ_COORD();
	m_mohaaCompassTarget[2] = READ_COORD();
	return 1;
}

int CHudDod::MsgFunc_DodHud( const char *pszName, int iSize, void *pbuf )
{
	int owners_lo;

	BEGIN_READ( pbuf, iSize );
	m_state.allies_score = (short)READ_SHORT();
	m_state.axis_score = (short)READ_SHORT();
	m_state.round_number = (unsigned char)READ_BYTE();
	m_state.rounds_to_win = (unsigned char)READ_BYTE();
	m_state.won_allies = (unsigned char)READ_BYTE();
	m_state.won_axis = (unsigned char)READ_BYTE();
	m_state.seconds_left = (short)READ_SHORT();
	m_state.phase = (unsigned char)READ_BYTE();
	m_state.num_points = (unsigned char)READ_BYTE();
	owners_lo = READ_SHORT();
	m_state.owners = (unsigned short)owners_lo;
	m_state.my_team = (unsigned char)READ_BYTE();
	m_state.my_class = (unsigned char)READ_BYTE();
	m_state.grenades = (unsigned char)READ_BYTE();
	m_state.kit = (unsigned char)READ_BYTE();
	m_state.stamina = (unsigned char)READ_BYTE();
	m_state.respawn = (unsigned char)READ_BYTE();
	m_flLastUpdate = m_flTimerBase = gEngfuncs.GetClientTime();
	m_fHaveState = 1;
	return 1;
}

/* The server sends the scoreboard text (Dod_FormatScoreboard) once a second while the player has it open, and an
 * empty one to close it. */
int CHudDod::MsgFunc_DodBoard( const char *pszName, int iSize, void *pbuf )
{
	int show;
	const char *text;

	BEGIN_READ( pbuf, iSize );
	show = READ_BYTE();
	text = show ? READ_STRING() : "";
	strncpy( m_szBoard, show && text ? text : "", sizeof( m_szBoard ) - 1 );
	m_szBoard[sizeof( m_szBoard ) - 1] = 0;
	m_flBoardTime = gEngfuncs.GetClientTime();
	m_fBoardShown = show && m_szBoard[0];
	return 1;
}

/* The kill feed: killer, victim, weapon; the last five are kept and each shows for 6 seconds. */
int CHudDod::MsgFunc_DodKill( const char *pszName, int iSize, void *pbuf )
{
	KillLine line;

	BEGIN_READ( pbuf, iSize );
	line.killer_team = READ_BYTE();
	strncpy( line.killer, READ_STRING(), sizeof( line.killer ) - 1 );
	line.killer[sizeof( line.killer ) - 1] = 0;
	line.victim_team = READ_BYTE();
	strncpy( line.victim, READ_STRING(), sizeof( line.victim ) - 1 );
	line.victim[sizeof( line.victim ) - 1] = 0;
	strncpy( line.weapon, READ_STRING(), sizeof( line.weapon ) - 1 );
	line.weapon[sizeof( line.weapon ) - 1] = 0;
	line.time = gEngfuncs.GetClientTime();
	if( m_nKills == DOD_HUD_KILL_LINES )
	{
		memmove( &m_kills[0], &m_kills[1], sizeof( KillLine ) * ( DOD_HUD_KILL_LINES - 1 ));
		m_nKills = DOD_HUD_KILL_LINES - 1;
	}
	m_kills[m_nKills++] = line;
	return 1;
}

static float g_flChatInputTime = -10.0f;

void DodHud_ChatInputPosition( int *x, int *y )
{
	const float sx = ( ScreenWidth > 0 ? ScreenWidth : 640 ) / 640.0f, sy = ( ScreenHeight > 0 ? ScreenHeight : 480 ) / 480.0f;
	const DodRect r = Dod_HudChatInput( DOD_HUD_LINE_H );

	g_flChatInputTime = gEngfuncs.GetClientTime();
	*x = (int)( r.x * sx + 0.5f );
	*y = (int)( r.y * sy + 0.5f );
}

int CHudDod::Modal( void )
{
	const float now = gEngfuncs.GetClientTime();

	/* the chat prompt asked for a position, or the on-screen keyboard is up (it covers the bottom of the screen) */
	m_fChatting = now - g_flChatInputTime < 0.3f || gEngfuncs.pfnGetCvarFloat( "gc_osk_open" ) != 0.0f;
	return m_fChatting || gHUD.m_Menu.m_fMenuDisplayed || ( m_fBoardShown && now - m_flBoardTime <= 3.0f )
		|| ( m_fVoiceShown && now - m_flVoiceTime <= 9.0f );
}

void CHudDod::DrawKills( void )
{
	const int line_h = gHUD.m_scrinfo.iCharHeight > 0 ? gHUD.m_scrinfo.iCharHeight : 12;
	const int w = ScreenWidth > 0 ? ScreenWidth : 320;
	const float now = gEngfuncs.GetClientTime();
	const float gsy = ( ScreenHeight > 0 ? ScreenHeight : 480 ) / 480.0f;
	int i, y = (int)( Dod_HudModalTop() * gsy + 0.5f ), drawn = 0;

	/* Spectators get the objective bar lower (retail CObjectiveIcons: 54 px down at 640x480, flags 2 * 54):
	 * its flags span 54..70 at this HUD size, so start the feed below them instead of across them. */
	if( g_iUser1 != 0 )
	{
		const int sh = ScreenHeight > 0 ? ScreenHeight : 240;
		const int flags_bottom = (int)(( 2.0f * 54.0f + 32.0f ) * ( sh / 480.0f ) + 0.5f ); // layout is 640x480, drawn scaled

		if( y < flags_bottom + 4 )
			y = flags_bottom + 4;
	}

	/* the oldest expired lines drop off */
	while( m_nKills > 0 && now - m_kills[0].time > 6.0f )
	{
		memmove( &m_kills[0], &m_kills[1], sizeof( KillLine ) * ( m_nKills - 1 ));
		m_nKills--;
	}
	const int safe_x = w / 20 > 6 ? w / 20 : 6; // 5% title-safe
	for( i = 0; i < m_nKills; i++ )
	{
		char text[110];
		const KillLine &k = m_kills[i];
		int r = 255, g = 255, b = 255;

		if( k.killer[0] )
			sprintf( text, "%s - %s - %s", k.killer, k.weapon, k.victim );
		else
			sprintf( text, "%s - %s", k.victim, k.weapon );
		/* the victim's side colours the line: Allies green, Axis red */
		if( k.victim_team == 1 ) { r = 150; g = 230; b = 150; }
		else if( k.victim_team == 2 ) { r = 235; g = 140; b = 140; }
		gHUD.DrawHudString( safe_x, y, w - safe_x, text, r, g, b );
		y += line_h;
		drawn++;
	}
	(void)drawn;
}

/* The voice menu (Y on the pad): the server sends the lines and the highlighted one whenever it changes. */
int CHudDod::MsgFunc_DodVoice( const char *pszName, int iSize, void *pbuf )
{
	int show;

	BEGIN_READ( pbuf, iSize );
	show = READ_BYTE();
	m_iVoiceSel = show ? READ_BYTE() : 0;
	strncpy( m_szVoice, show ? READ_STRING() : "", sizeof( m_szVoice ) - 1 );
	m_szVoice[sizeof( m_szVoice ) - 1] = 0;
	m_flVoiceTime = gEngfuncs.GetClientTime();
	m_fVoiceShown = show && m_szVoice[0];
	return 1;
}

void CHudDod::DrawVoice( void )
{
	char line[48];
	const char *p = m_szVoice;
	const int line_h = gHUD.m_scrinfo.iCharHeight > 0 ? gHUD.m_scrinfo.iCharHeight : 12;
	const int w = ScreenWidth > 0 ? ScreenWidth : 640, h = ScreenHeight > 0 ? ScreenHeight : 480;
	const float gsx = w / 640.0f, gsy = h / 480.0f;
	const int glh = (int)( line_h / gsy + 0.5f ), pad = 8;
	int rows = 0, maxw, x0, y0, pw, ph, y, row = 0, show, first;
	DodRect pr;

	if( !m_fVoiceShown || gEngfuncs.GetClientTime() - m_flVoiceTime > 9.0f )
		return;
	/* the widest line, the rows the band can hold (the list scrolls to keep the chosen row in view) */
	maxw = gHUD.DrawHudStringLen( "Voice" );
	for( const char *q = p; *q; )
	{
		char tmp[48];
		int n = 0;

		while( q[n] && q[n] != '\n' && n < (int)sizeof( tmp ) - 1 ) { tmp[n] = q[n]; n++; }
		tmp[n] = 0;
		q += n;
		if( *q == '\n' ) q++;
		if( gHUD.DrawHudStringLen( tmp ) > maxw ) maxw = gHUD.DrawHudStringLen( tmp );
		rows++;
	}
	show = rows + 1 > Dod_HudModalRows( glh ) ? Dod_HudModalRows( glh ) : rows + 1;	/* with the title */
	first = m_iVoiceSel - ( show - 1 ) / 2;
	if( first > rows - ( show - 1 )) first = rows - ( show - 1 );
	if( first < 0 ) first = 0;
	pr = Dod_HudCentredPanel( show, (int)( maxw / gsx + 0.5f ), glh );
	x0 = (int)( pr.x * gsx + 0.5f );
	y0 = (int)( pr.y * gsy + 0.5f );
	pw = (int)( pr.w * gsx + 0.5f );
	ph = (int)( pr.h * gsy + 0.5f );
	gEngfuncs.pfnFillRGBABlend( x0, y0, pw, ph, 0, 0, 0, 170 );
	gEngfuncs.pfnFillRGBABlend( x0, y0, pw, 1, 200, 200, 200, 160 );
	gEngfuncs.pfnFillRGBABlend( x0, y0 + ph - 1, pw, 1, 200, 200, 200, 160 );
	gEngfuncs.pfnFillRGBABlend( x0, y0, 1, ph, 200, 200, 200, 160 );
	gEngfuncs.pfnFillRGBABlend( x0 + pw - 1, y0, 1, ph, 200, 200, 200, 160 );
	y = y0 + (int)( DOD_HUD_PANEL_PAD * gsy + 0.5f );
	(void)pad;
	gHUD.DrawHudString( x0 + pad, y, x0 + pw - pad, "Voice", 255, 255, 255 );
	y += line_h;
	while( *p )
	{
		int n = 0;
		const int sel = row == m_iVoiceSel;

		while( p[n] && p[n] != '\n' && n < (int)sizeof( line ) - 1 )
		{
			line[n] = p[n];
			n++;
		}
		line[n] = 0;
		p += n;
		if( *p == '\n' ) p++;
		if( row >= first && row < first + show - 1 )
		{
			/* the chosen line sits on a bar (the HUD font has no marker glyph that reads well) */
			if( sel )
				gEngfuncs.pfnFillRGBABlend( x0 + 2, y - 1, pw - 4, line_h, 255, 230, 90, 70 );
			gHUD.DrawHudString( x0 + pad, y, x0 + pw - pad, line, sel ? 255 : 220, sel ? 230 : 220, sel ? 90 : 220 );
			y += line_h;
		}
		row++;
	}
}

void CHudDod::DrawBoard( void )
{
	/* A centred panel, as the retail scoreboard: the title, then a team header with its score and the team's players
	 * ranked, name and class on the left and Score/Kills/Deaths against the right edge. */
	char line[96], left[96];
	const char *p = m_szBoard;
	const int line_h = gHUD.m_scrinfo.iCharHeight > 0 ? gHUD.m_scrinfo.iCharHeight : 12;
	const int w = ScreenWidth > 0 ? ScreenWidth : 320, h = ScreenHeight > 0 ? ScreenHeight : 240;
	const float gsx = w / 640.0f, gsy = h / 480.0f;
	const int pad = 8;
	int pw, rows = 0, gaps = 0, ph, x0, y0, y, y_end;
	DodRect pr;

	if( !m_fBoardShown || gEngfuncs.GetClientTime() - m_flBoardTime > 3.0f )
		return;
	for( const char *q = p; *q; q++ )
	{
		if( *q == '\n' && q[1] == '\n' ) gaps++;
		else if( *q == '\n' && q[1] ) rows++;
	}
	rows++;	/* the first line has no newline before it */
	ph = ( rows + 1 ) * line_h + gaps * ( line_h / 2 ) + 2 * pad;	/* + the title */
	/* centred in the band under the objective row and above the status panel; rows beyond it are not drawn */
	pr = Dod_HudCentredPanel(( ph + (int)( DOD_HUD_LINE_H * gsy ) - 1 ) / (int)( DOD_HUD_LINE_H * gsy ), 520, DOD_HUD_LINE_H );
	x0 = (int)( pr.x * gsx + 0.5f );
	y0 = (int)( pr.y * gsy + 0.5f );
	pw = (int)( pr.w * gsx + 0.5f );
	if( ph > (int)( pr.h * gsy )) ph = (int)( pr.h * gsy );
	y_end = y0 + ph - pad;
	gEngfuncs.pfnFillRGBABlend( x0, y0, pw, ph, 0, 0, 0, 170 );
	/* a 1 px border */
	gEngfuncs.pfnFillRGBABlend( x0, y0, pw, 1, 200, 200, 200, 160 );
	gEngfuncs.pfnFillRGBABlend( x0, y0 + ph - 1, pw, 1, 200, 200, 200, 160 );
	gEngfuncs.pfnFillRGBABlend( x0, y0, 1, ph, 200, 200, 200, 160 );
	gEngfuncs.pfnFillRGBABlend( x0 + pw - 1, y0, 1, ph, 200, 200, 200, 160 );
	y = y0 + pad;
	{
		const char *title = "Scoreboard";
		gHUD.DrawHudString( x0 + ( pw - gHUD.DrawHudStringLen( title )) / 2, y, x0 + pw, title, 255, 255, 255 );
		y += line_h;
	}
	while( *p )
	{
		int n = 0, r = 255, g = 255, b = 255, split = -1, i;

		while( p[n] && p[n] != '\n' && n < (int)sizeof( line ) - 1 )
		{
			line[n] = p[n];
			n++;
		}
		line[n] = 0;
		p += n;
		if( *p == '\n' ) p++;
		if( !n ) { y += line_h / 2; continue; }
		if( y + line_h > y_end ) break;	/* the rest does not fit the panel */
		if( !strncmp( line, "Allies", 6 )) { r = 140; g = 230; b = 140; }
		else if( !strncmp( line, "Axis", 4 )) { r = 235; g = 130; b = 130; }
		else if( line[0] == '>' )
		{
			r = 255; g = 230; b = 90;
			memmove( line, line + 1, n );	/* the viewer's row: a bar instead of the marker glyph */
			n--;
			gEngfuncs.pfnFillRGBABlend( x0 + 2, y - 1, pw - 4, line_h, 255, 230, 90, 60 );
		}
		/* where the right-hand part starts: the score after a team name, S.. K.. D.. after a player */
		if( !strncmp( line, "Allies", 6 ) || !strncmp( line, "Axis", 4 ))
		{
			for( i = 0; line[i]; i++ )
				if( line[i] == ' ' && line[i + 1] == ' ' ) { split = i; break; }
		}
		else
		{
			for( i = n - 1; i > 1; i-- )
				if( line[i] == 'S' && line[i - 1] == ' ' && line[i - 2] == ' ' ) { split = i - 2; break; }
		}
		if( split > 0 )
		{
			const char *right = line + split;
			while( *right == ' ' ) right++;
			strncpy( left, line, split );
			left[split] = 0;
			gHUD.DrawHudString( x0 + pad, y, x0 + pw - pad, left, r, g, b );
			gHUD.DrawHudStringReverse( x0 + pw - pad, y, x0 + pad, right, r, g, b );
		}
		else
			gHUD.DrawHudString( x0 + pad, y, x0 + pw - pad, line, r, g, b );
		y += line_h;
	}
}

int CHudDod::DrawRetail( float flTime )
{
	gEngfuncs.Cvar_SetValue( "gc_hud_retail", 0.0f );
	DodRetailInput in;
	DodRetailDraw draws[DOD_RETAIL_MAX_DRAWS];
	DodRetailText spare;
	const WEAPON *pw;
	int count, i, drawn = 0;

	if( !m_pCvar || m_pCvar->value == 0.0f )
		return 0;

	/* The sheets load the first time the HUD draws (SPR_Load on demand). */
	if( !m_fSheetsTried )
	{
		m_fSheetsTried = 1;
		/* The always-on pieces load now; the clip and rocket sheets (65 KB
		 * each while loading) only when a gun that uses them is held. */
		for( i = 0; i < DOD_SHEET_COUNT; i++ )
		{
			m_hSheets[i] = 0;
			if( Dod_RetailSheetAlwaysOn( i ))
			{
				m_fSheetTried |= 1u << i;
				m_hSheets[i] = SPR_Load( dod_retail_sheet_files[i] );
			}
		}
		gEngfuncs.Con_Printf( "Xash3D GameCube: DoD retail HUD sheets layout=%d cross=%d\n",
			m_hSheets[DOD_SHEET_LAYOUT] ? 1 : 0, m_hSheets[DOD_SHEET_CROSS] ? 1 : 0 );
		for( i = 0; i < DOD_SHEET_COUNT; i++ )
			gEngfuncs.Con_Printf( "Xash3D GameCube: DoD retail HUD sheet %s h=%d %dx%d\n",
				dod_retail_sheet_files[i], m_hSheets[i],
				m_hSheets[i] ? SPR_Width( m_hSheets[i], 0 ) : 0,
				m_hSheets[i] ? SPR_Height( m_hSheets[i], 0 ) : 0 );
	}
	if( !m_hSheets[DOD_SHEET_LAYOUT] )
		return 0;	/* no retail sheets on this disc: let the caller draw */
	if( gHUD.m_iHideHUDDisplay & HIDEHUD_ALL )
	{
		/* a MOHAA cutscene's "drawhud 0": nothing, and nothing else may draw health or ammo either */
		gEngfuncs.Cvar_SetValue( "gc_hud_retail", 1.0f );
		return 1;
	}

	/* Retail lays the 640-res art out 1:1 on a 640x480 screen. The GameCube
	 * HUD space is 320x240 (shown at 2x), so lay out at 640x480 and scale
	 * every draw by the HUD space's share of that. */
	const int hud_w = ScreenWidth > 0 ? ScreenWidth : 640;
	const int hud_h = ScreenHeight > 0 ? ScreenHeight : 480;
	const float sx = hud_w / 640.0f, sy = hud_h / 480.0f;

	memset( &in, 0, sizeof( in ) );
	in.screen_w = 640;
	in.screen_h = 480;
	/* title-safe area: about 5% off the right and bottom edges so the ammo block is not lost to TV overscan or the
	 * output edge. The text width is measured in the HUD font (wider than retail's at 640). */
	in.safe_left = in.safe_right = 32;
	in.safe_top = in.safe_bottom = 24;
	in.text_w = (int)( gHUD.DrawHudStringLen( "x 99" ) / sx + 0.5f );
	in.text_h = (int)( ( gHUD.m_scrinfo.iCharHeight > 0 ? gHUD.m_scrinfo.iCharHeight : 12 ) / sy + 0.5f );
	Modal();
	in.hide_bottom = m_fChatting;
	in.hide_objectives = gHUD.m_Menu.m_fMenuDisplayed;
	in.health = gHUD.m_Health.m_iHealth;
	in.stamina = m_fHaveState ? (float)m_state.stamina : 100.0f;
	in.spectating = g_iUser1 != 0;
	in.dead = in.health <= 0;
	in.show_reinforcements = 0;
	/* a MOHAA scripted ride (player locked): no crosshair or ammo, as retail shows none there */
	in.crosshair = ( gHUD.m_iHideHUDDisplay & HIDEHUD_WEAPONS ) ? 0 : 1;
	if( gHUD.m_iHideHUDDisplay & HIDEHUD_WEAPONS )
		in.hide_bottom = 1;
	in.crosshair_gap = 4;
	/* The server sends the clock a couple of times a second; count down
	 * between messages, and hide it when the messages stop. */
	in.seconds_left = -1;
	if( m_fHaveState && m_state.seconds_left > 0
		&& gEngfuncs.GetClientTime() - m_flLastUpdate <= 4.0f )
	{
		const int left = m_state.seconds_left - (int)( gEngfuncs.GetClientTime() - m_flTimerBase );
		in.seconds_left = left > 0 ? left : 0;
	}

	/* Capture points from the DodHud message, left to right. */
	if( m_fHaveState )
	{
		in.num_points = m_state.num_points < DOD_HUD_MAX_POINTS ? m_state.num_points : DOD_HUD_MAX_POINTS;
		for( i = 0; i < in.num_points; i++ )
			in.owner[i] = Dod_HudOwnerOf( m_state.owners, i );
	}

	/* Clip ammo: the held weapon's magazine graphic and spare clips. */
	pw = gHUD.m_Ammo.GetCurrentWeapon();
	if( pw && pw->iClip >= 0 )
	{
		in.weapon = Dod_RetailClipForKit( pw->szName, m_fHaveState ? m_state.kit : 0 );
		in.clip = pw->iClip;
		in.reserve = pw->iAmmoType > 0 ? gWR.CountAmmo( pw->iAmmoType ) : 0;
	}

	count = Dod_RetailHudLayoutText( &in, draws, DOD_RETAIL_MAX_DRAWS, &spare );
	{
		/* Log each weapon change once (which clip graphic, if any, is drawn). */
		const char *name = pw ? pw->szName : "-";
		if( strncmp( m_szLoggedWeapon, name, sizeof( m_szLoggedWeapon ) - 1 ))
		{
			strncpy( m_szLoggedWeapon, name, sizeof( m_szLoggedWeapon ) - 1 );
			m_szLoggedWeapon[sizeof( m_szLoggedWeapon ) - 1] = 0;
			gEngfuncs.Con_Printf( "Xash3D GameCube: DoD retail HUD weapon %s clip=%d reserve=%d graphic=%s draws=%d\n",
				name, in.clip, in.reserve, in.weapon ? in.weapon->key : "-", count );
		}
	}
	for( i = 0; i < count; i++ )
	{
		const int sheet = draws[i].cell.sheet;
		wrect_t rc;

		if( !m_hSheets[sheet] && !( m_fSheetTried & ( 1u << sheet )))
		{
			m_fSheetTried |= 1u << sheet;
			m_hSheets[sheet] = SPR_Load( dod_retail_sheet_files[sheet] );
			gEngfuncs.Con_Printf( "Xash3D GameCube: DoD retail HUD sheet %s loaded on use h=%d\n",
				dod_retail_sheet_files[sheet], m_hSheets[sheet] );
		}
		const HSPRITE spr = m_hSheets[sheet];

		if( !spr )
			continue;
		rc.left = draws[i].cell.x;
		rc.right = draws[i].cell.x + draws[i].cell.w;
		rc.top = draws[i].cell.y;
		rc.bottom = draws[i].cell.y + draws[i].cell.h;
		SPR_Set( spr, 255, 255, 255 );
		if( sx == 1.0f && sy == 1.0f )
			SPR_DrawHoles( 0, draws[i].x, draws[i].y, &rc );
		else
		{
			/* Snap both edges so neighbouring pieces still meet. */
			const int x0 = (int)( draws[i].x * sx + 0.5f );
			const int y0 = (int)( draws[i].y * sy + 0.5f );
			int w = (int)(( draws[i].x + draws[i].cell.w ) * sx + 0.5f ) - x0;
			int h = (int)(( draws[i].y + draws[i].cell.h ) * sy + 0.5f ) - y0;

			if( w < 1 ) w = 1;
			if( h < 1 ) h = 1;
			gEngfuncs.pfnSPR_DrawGeneric( 0, x0, y0, &rc, 0, 0, w, h );
		}
		drawn++;
	}
	if( spare.count > 0 && spare.x >= 0 )
	{
		/* retail: DrawHudString( x, base, x + 64, "x %d", white ) */
		char buf[16];
		const int tx = (int)( spare.x * sx + 0.5f );

		sprintf( buf, "x %d", spare.count );
		gHUD.DrawHudString( tx, (int)( spare.y * sy + 0.5f ), tx + (int)( 64 * sx + 0.5f ), buf, 255, 255, 255 );
	}
	DrawBoard();
	DrawVoice();
	/* The feed is drawn last, so it ran across the centred scoreboard and voice menu panels (both overlap its
	 * x 6..w, y 62.. rows); it waits until they close. */
	if( !Modal( ))
		DrawKills();
	/* a dead player waits for the next wave of their side */
	if( m_fHaveState && m_state.respawn > 0 && gHUD.m_Health.m_iHealth <= 0 && gEngfuncs.GetClientTime() - m_flLastUpdate < 3.0f )
	{
		char text[40];
		const int w = ScreenWidth > 0 ? ScreenWidth : 320, h = ScreenHeight > 0 ? ScreenHeight : 240;
		const int n = sprintf( text, "Respawn in %d", (int)m_state.respawn );

		const DodRect rr = Dod_HudRespawnText( DOD_HUD_LINE_H );

		gHUD.DrawHudString( (int)( rr.x * w / 640.0f + 0.5f ), (int)( rr.y * h / 480.0f + 0.5f ), w, text, 255, 255, 255 );
		(void)n;
	}
	if( !m_fDrawLogged )
	{
		m_fDrawLogged = 1;
		gEngfuncs.Con_Printf( "Xash3D GameCube: DoD retail HUD drew %d/%d health=%d timer=%d weapon=%s\n",
			drawn, count, in.health, in.seconds_left, in.weapon ? in.weapon->key : "-" );
	}
	gEngfuncs.Cvar_SetValue( "gc_hud_retail", 1.0f );	/* the retail readout drew this frame: nothing else may draw ammo or health */
	return 1;
}

static int mohaa_frame16( float degrees )
{
	int frame = (int)( degrees * ( 16.0f / 360.0f ) + ( degrees >= 0.0f ? 0.5f : -0.5f ));
	frame %= 16;
	if( frame < 0 ) frame += 16;
	return frame;
}

static float mohaa_clamp01( float value )
{
	if( value < 0.0f ) return 0.0f;
	if( value > 1.0f ) return 1.0f;
	return value;
}

static void mohaa_draw_compass_layer( HSPRITE sprite, int frame, int x, int y, int width, int height )
{
	int source_width, source_height;
	wrect_t source;
	if( !sprite )
		return;
	source_width = SPR_Width( sprite, frame );
	source_height = SPR_Height( sprite, frame );
	if( source_width <= 0 || source_height <= 0 )
		return;
	source.left = source.top = 0;
	source.right = source_width;
	source.bottom = source_height;
	SPR_Set( sprite, 255, 255, 255 );
	gEngfuncs.pfnSPR_DrawGeneric( frame, x, y, &source, 0, 0, width, height );
}

/* iprintlnbold has no explicit width. Wrap at the active client font's pixel
 * widths so long retail tips stay inside the visible GameCube viewport. */
static void mohaa_wrap_hint( char *text, int max_width )
{
	char *line = text;
	while( *line )
	{
		char *p = line, *last_space = NULL;
		int width = 0;
		while( *p && *p != '\n' )
		{
			char glyph[2] = { *p, 0 };
			int char_width = 0;
			gEngfuncs.pfnDrawConsoleStringLen( glyph, &char_width, NULL );
			if( width + char_width > max_width )
				break;
			if( *p == ' ' )
				last_space = p;
			width += char_width;
			p++;
		}
		if( *p == '\n' )
			line = p + 1;
		else if( *p )
		{
			if( last_space )
			{
				*last_space = '\n';
				line = last_space + 1;
			}
			else
				line = p + 1;
		}
		else
			break;
	}
}

int CHudDod::DrawMohaa( float flTime )
{
	const int screen_w = ScreenWidth > 0 ? ScreenWidth : 320;
	const int screen_h = ScreenHeight > 0 ? ScreenHeight : 240;
	const int line_h = gHUD.m_scrinfo.iCharHeight > 0 ? gHUD.m_scrinfo.iCharHeight : 10;
	float view[3] = {0, 0, 0};
	float yaw = 0.0f;
	int i;
	int hint_line_h = line_h;
	(void)flTime;
	if( !HUD_IsGame( "mohaa" ) )
		return 0;
	if( gHUD.m_iHideHUDDisplay & HIDEHUD_ALL )
		return 1;
	if( !m_mohaaCompassTried )
	{
		m_mohaaCompassTried = 1;
		m_hMohaaCompassBack = SPR_Load( "sprites/mohaa/compassback.spr" );
		m_hMohaaCompassFace = SPR_Load( "sprites/mohaa/compassface.spr" );
		m_hMohaaCompassNeedle = SPR_Load( "sprites/mohaa/compassneedle.spr" );
		m_hMohaaCompassObjective = SPR_Load( "sprites/mohaa/compassobjarrow.spr" );
	}
	gEngfuncs.GetViewAngles( view );
	yaw = view[1];
	while( yaw < 0.0f ) yaw += 360.0f;
	while( yaw >= 360.0f ) yaw -= 360.0f;
	{
		const int x = (int)( 4.0f * screen_w / 320.0f + 0.5f );
		const int y = (int)( 3.0f * screen_h / 240.0f + 0.5f );
		const int width = (int)( 55.0f * screen_w / 320.0f + 0.5f );
		const int height = (int)( 55.0f * screen_h / 240.0f + 0.5f );
		mohaa_draw_compass_layer( m_hMohaaCompassBack, 0, x, y, width, height );
		mohaa_draw_compass_layer( m_hMohaaCompassFace, mohaa_frame16( yaw ), x, y, width, height );
		if( m_hMohaaCompassObjective && m_mohaaCompassHasTarget )
		{
			cl_entity_t *player = gEngfuncs.GetLocalPlayer();
			if( player )
			{
				const float dx = m_mohaaCompassTarget[0] - player->origin[0];
				const float dy = m_mohaaCompassTarget[1] - player->origin[1];
				const float target_yaw = (float)( atan2( dy, dx ) * ( 180.0 / 3.14159265358979323846 ));
				mohaa_draw_compass_layer( m_hMohaaCompassObjective,
					mohaa_frame16( yaw - target_yaw ), x, y, width, height );
			}
		}
		mohaa_draw_compass_layer( m_hMohaaCompassNeedle, 0, x, y, width, height );
	}

	/* Scripted shader cards (the gas-mask overlay, for example) sit above the compass. */
	for( i = 0; i < DOD_MOHAA_HUD_DRAW_COUNT; i++ )
	{
		DodMohaaHudDraw *d = &m_mohaaHud[i];
		if( !d->shader[0] || d->a <= 0.0f )
			continue;
		if( !m_mohaaHudShaderTried[i] )
		{
			char sprite[96], stem[64];
			const char *base = strrchr( d->shader, '/' );
			const char *ext;
			base = base ? base + 1 : d->shader;
			strncpy( stem, base, sizeof( stem ) - 1 ); stem[sizeof( stem ) - 1] = 0;
			ext = strrchr( stem, '.' ); if( ext ) ((char *)ext)[0] = 0;
			snprintf( sprite, sizeof( sprite ), "sprites/mohaa/%s.spr", stem );
			m_hMohaaHudShader[i] = SPR_Load( sprite );
			m_mohaaHudShaderTried[i] = 1;
		}
		if( m_hMohaaHudShader[i] )
		{
			const float sx = d->virtual_size ? screen_w / 640.0f : 1.0f;
			const float sy = d->virtual_size ? screen_h / 480.0f : 1.0f;
			const int sw = SPR_Width( m_hMohaaHudShader[i], 0 ), sh = SPR_Height( m_hMohaaHudShader[i], 0 );
			const int w = d->w > 0.0f ? (int)( d->w * sx + 0.5f ) : sw;
			const int h = d->h > 0.0f ? (int)( d->h * sy + 0.5f ) : sh;
			int x = (int)( d->x * sx + 0.5f ), y = (int)( d->y * sy + 0.5f );
			wrect_t rc = {0, 0, sw, sh};
			if( d->align_x == DOD_MOHAA_HUD_ALIGN_CENTER ) x += screen_w / 2 - w / 2;
			else if( d->align_x == DOD_MOHAA_HUD_ALIGN_RIGHT ) x += screen_w - w;
			if( d->align_y == DOD_MOHAA_HUD_ALIGN_MIDDLE ) y += screen_h / 2 - h / 2;
			else if( d->align_y == DOD_MOHAA_HUD_ALIGN_BOTTOM ) y += screen_h - h;
			SPR_Set( m_hMohaaHudShader[i], (int)( d->r * d->a * 255.0f ),
				(int)( d->g * d->a * 255.0f ), (int)( d->b * d->a * 255.0f ) );
			gEngfuncs.pfnSPR_DrawGeneric( 0, x, y, &rc, 0, 0, w, h );
		}
	}

	/* Retail huddraw text supports independent slots, alignment, RGB and fade alpha. */
	for( i = 0; i < DOD_MOHAA_HUD_DRAW_COUNT; i++ )
	{
		DodMohaaHudDraw *d = &m_mohaaHud[i];
		char text[DOD_MOHAA_HUD_TEXT];
		char *line;
		const float sx = d->virtual_size ? screen_w / 640.0f : 1.0f;
		const float sy = d->virtual_size ? screen_h / 480.0f : 1.0f;
		int y_anchor, y, line_no = 0;
		float draw_alpha = d->a;
		int cr, cg, cb;
		if( !d->text[0] || d->a <= 0.0f )
			continue;
		if( i == DOD_MOHAA_HUD_HINT_INDEX )
		{
			const float remaining = m_flMohaaHintUntil - flTime;
			if( remaining <= 0.0f )
				continue;
			if( remaining < 0.5f )
				draw_alpha *= remaining / 0.5f;
		}
		cr = (int)( mohaa_clamp01( d->r * draw_alpha ) * 255.0f + 0.5f );
		cg = (int)( mohaa_clamp01( d->g * draw_alpha ) * 255.0f + 0.5f );
		cb = (int)( mohaa_clamp01( d->b * draw_alpha ) * 255.0f + 0.5f );
		strncpy( text, d->text, sizeof( text ) - 1 ); text[sizeof( text ) - 1] = 0;
		if( i == DOD_MOHAA_HUD_HINT_INDEX )
		{
			const int left = (int)( d->x * sx + 0.5f );
			const int right_margin = 8;
			/* Ensure the engine's one-shot scale cvar exists before setting it. */
			gEngfuncs.pfnDrawConsoleStringLen( "M", NULL, &hint_line_h );
			gEngfuncs.Cvar_SetValue( "gc_mohaa_hint_draw", 1.0f );
			gEngfuncs.pfnDrawConsoleStringLen( "M", NULL, &hint_line_h );
			if( hint_line_h < 1 ) hint_line_h = line_h;
			mohaa_wrap_hint( text, screen_w > left + right_margin ? screen_w - left - right_margin : screen_w );
		}
		for( line = text; *line; line++ ) if( *line == '\n' ) line_no++;
		line_no++;
		y_anchor = (int)( d->y * sy + 0.5f );
		if( d->align_y == DOD_MOHAA_HUD_ALIGN_MIDDLE ) y_anchor = screen_h / 2 + y_anchor;
		else if( d->align_y == DOD_MOHAA_HUD_ALIGN_BOTTOM ) y_anchor = screen_h - y_anchor;
		if( d->align_y == DOD_MOHAA_HUD_ALIGN_MIDDLE ) y_anchor -= ( line_no * ( i == DOD_MOHAA_HUD_HINT_INDEX ? hint_line_h : line_h )) / 2;
		else if( d->align_y == DOD_MOHAA_HUD_ALIGN_BOTTOM ) y_anchor -= line_no * ( i == DOD_MOHAA_HUD_HINT_INDEX ? hint_line_h : line_h );
		y = y_anchor;
		line = text;
		while( line )
		{
			char *next = strchr( line, '\n' );
			int width, x_anchor, x;
			if( next ) *next = 0;
			width = gHUD.DrawHudStringLen( line );
			x_anchor = (int)( d->x * sx + 0.5f );
			if( d->align_x == DOD_MOHAA_HUD_ALIGN_CENTER ) x_anchor += screen_w / 2;
			else if( d->align_x == DOD_MOHAA_HUD_ALIGN_RIGHT ) x_anchor += screen_w;
			x = x_anchor;
			if( d->align_x == DOD_MOHAA_HUD_ALIGN_CENTER ) x -= width / 2;
			else if( d->align_x == DOD_MOHAA_HUD_ALIGN_RIGHT ) x -= width;
			if( i == DOD_MOHAA_HUD_HINT_INDEX )
			{
				/* Retail tips use a compact scale of the credits face. */
				char draw_line[ DOD_MOHAA_HUD_TEXT ];
				strncpy( draw_line, line, sizeof( draw_line ) - 1 );
				draw_line[ sizeof( draw_line ) - 1 ] = 0;
				gEngfuncs.pfnDrawSetTextColor( 24.0f / 255.0f, 18.0f / 255.0f, 12.0f / 255.0f );
				gEngfuncs.pfnDrawConsoleString( x + 1, y + 1, draw_line );
				gEngfuncs.pfnDrawSetTextColor( cr / 255.0f, cg / 255.0f, cb / 255.0f );
				gEngfuncs.pfnDrawConsoleString( x, y, draw_line );
			}
			else
				gHUD.DrawHudString( x, y, screen_w, line, cr, cg, cb );
			y += i == DOD_MOHAA_HUD_HINT_INDEX ? hint_line_h : line_h;
			line = next ? next + 1 : NULL;
		}
		if( i == DOD_MOHAA_HUD_HINT_INDEX )
			gEngfuncs.Cvar_SetValue( "gc_mohaa_hint_draw", 0.0f );
	}
	/* Quality 0 bypasses CHud's HUD-element list; keep native HudText visible. */
	gHUD.m_Message.Draw( flTime );
	return 1;
}

int CHudDod::Draw( float flTime )
{
	if( HUD_IsGame( "mohaa" ) )
		DrawMohaa( flTime );
	else
		DrawRetail( flTime );
	return 1;
}
