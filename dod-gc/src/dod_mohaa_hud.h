/* Shared MOHAA HUD draw state sent from the game DLL to the client HUD. */
#ifndef DODGC_MOHAA_HUD_H
#define DODGC_MOHAA_HUD_H

#define DOD_MOHAA_HUD_DRAW_COUNT 255 /* wire index 255 is the clear-all marker */
#define DOD_MOHAA_HUD_HINT_INDEX 254 /* reserved for retail iprintlnbold hints */
#define DOD_MOHAA_HUD_TEXT 128
#define DOD_MOHAA_HUD_SHADER 64

enum {
	DOD_MOHAA_HUD_ALIGN_LEFT = 0,
	DOD_MOHAA_HUD_ALIGN_CENTER,
	DOD_MOHAA_HUD_ALIGN_RIGHT
};

enum {
	DOD_MOHAA_HUD_ALIGN_TOP = 0,
	DOD_MOHAA_HUD_ALIGN_MIDDLE,
	DOD_MOHAA_HUD_ALIGN_BOTTOM
};

typedef struct DodMohaaHudDraw {
	float x, y, w, h;
	float r, g, b, a;
	int align_x, align_y;
	int virtual_size;
	int initialized;
	char text[DOD_MOHAA_HUD_TEXT];
	char shader[DOD_MOHAA_HUD_SHADER];
} DodMohaaHudDraw;

#endif
