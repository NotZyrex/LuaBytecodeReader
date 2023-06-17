echo off
cls
title Dumping Bytecode...
"./lua/luac.exe" "./lua/input.lua"
title Bytecode Reader
py main.py