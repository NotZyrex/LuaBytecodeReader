echo off
title Bytecode Reader
cls
pip install -r requirements.txt
cls
"./lua/luac.exe" "./lua/input.lua"
py main.py
