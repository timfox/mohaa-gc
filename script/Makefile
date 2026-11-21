# Morpheus script VM (MOHAA .scr) for DoD-GC. Host build of the VM and the
# msrun test runner. The game build compiles src/*.c directly.
CC      ?= cc
CFLAGS  ?= -std=c99 -O2 -g -Wall -Wextra -Wno-unused-parameter
CFLAGS  += -Iinclude
OUT     ?= ../out
SRC     := src/ms_value.c src/ms_compile.c src/ms_vm.c src/ms_builtins.c

all: $(OUT)/msrun

$(OUT)/msrun: $(SRC) tools/msrun.c include/morpheus.h src/ms_internal.h
	@mkdir -p $(OUT)
	$(CC) $(CFLAGS) -o $@ $(SRC) tools/msrun.c -lm

clean:
	rm -f $(OUT)/msrun

.PHONY: all clean
