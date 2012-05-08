#!/bin/bash

# set up paths and variables for MCR
LD_LIBRARY_PATH=/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/bin/glnx86:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/runtime/glnx86:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/os/glnx86:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386/native_threads:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386/server:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386:$LD_LIBRARY_PATH; export LD_LIBRARY_PATH

PATH=/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/runtime/glnx86:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/os/glnx86:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386/native_threads:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386/server:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386:$PATH; export PATH

XAPPLRESDIR=/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/X11/app-defaults; export XAPPLRESDIR

# adjust locale for MCR
LANG=

# make call to MCR, webDICE
time ./diceDriver /var/www/chicagowebdice/input.csv output.csv