#!/bin/bash

echo "Current Python path:"
which python
echo

echo "All Python installations:"
where python 2>/dev/null || echo "where command not found"
echo

echo "Python version attempt 1:"
python --version
echo

echo "Python version attempt 2:"
/c/Users/balma/AppData/Local/Programs/Python/Python312/python.exe --version
echo

echo "Virtual env path:"
echo $VIRTUAL_ENV
echo

echo "System PATH (formatted):"
echo $PATH | tr ':' '\n' 