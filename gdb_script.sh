#!/bin/bash


LINE=get_level4_PTEH_for_eosdt
LINE=282 #835

gdb -ex 'set breakpoint pending on' -ex 'dir ../CHIMES-repos/chimes/src' -ex "b init_chimes.c:${LINE}" -ex 'run' -ex r --args python runner.py

