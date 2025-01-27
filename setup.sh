#!/bin/bash

# Use Python312 explicitly
SYSTEM_PYTHON="/c/Users/balma/AppData/Local/Programs/Python/Python312/python.exe"

VENV_PATH="./venv"
echo "Creating virtual environment in $VENV_PATH"
"$SYSTEM_PYTHON" -m venv $VENV_PATH

echo -e "\nActivating virtual environment..."
source $VENV_PATH/Scripts/activate

if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

PYTHON_PATH="$VENV_PATH/Scripts/python.exe"
echo "Using Python at: $PYTHON_PATH"

echo -e "\nUpgrading pip..."
"$PYTHON_PATH" -m pip install --upgrade pip

echo -e "\nInstalling requirements..."
"$PYTHON_PATH" -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit 1
fi

echo -e "\nRunning script..."
"$PYTHON_PATH" Photoshop_scripts/ps_scripts/single_folder_watermarking_only_script.py 