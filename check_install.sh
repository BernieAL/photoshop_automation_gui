#!/bin/bash

echo "Checking Python installation..."
if command -v python &>/dev/null; then
    echo "Python is installed at: $(which python)"
    python --version
else
    echo "Python is not installed"
fi

echo -e "\nChecking pip installation..."
if command -v pip &>/dev/null; then
    echo "pip is installed at: $(which pip)"
    pip --version
else
    echo "pip is not installed"
fi 