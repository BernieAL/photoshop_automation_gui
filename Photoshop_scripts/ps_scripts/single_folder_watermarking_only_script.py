#!/usr/bin/env python3
"""
Photoshop Watermarking Automation Script

This script automates the process of adding watermarks to images using Adobe Photoshop.
It processes all images in a SINGLE SPECIFIED folder and creates watermarked versions in an output directory.

Features:
    - Batch watermarking of images
    - Configurable watermark placement
    - Error logging with CSV output
    - Progress tracking

Technical Details:
    - Uses Photoshop COM automation through photoshop-python-api
    - Creates 'watermarked-output' subdirectory for processed images
    - Generates dated error logs in CSV format

Important Implementation Notes:
    1. Function Context:
        - All functions that interact with Photoshop MUST be nested within the Session context
        - Only utility functions can be outside context
        - All Photoshop interactions must use try/catch blocks
    
    2. Place Function ("Plc ") Requirements:
        - Requires an active document
        - Will fail if at Photoshop home screen
        - Must have document open before placing images

    3. Path Handling:
        - Windows uses backslashes, Unix uses forward slashes
        - Use os.path.join() for cross-platform compatibility
        - Convert paths using .replace("\\", "/") when needed

Requirements:
    - Adobe Photoshop CC or later (Confirmed working with PS 2022)
    - Python 3.11+
    - photoshop-python-api package
    - Photoshop must be running before script execution

Usage:
    Can be run directly or through GUI:
    - Direct: python single_folder_watermarking_only_script.py [folder_path]
    - GUI: Folder path will be provided through sys.argv[1]

Process Flow:
    1. Receives folder path (from GUI or command line)
    2. Creates 'watermarked-output' folder
    3. For each image:
        - Opens in Photoshop
        - Applies watermark
        - Saves to output folder
        - Cleans up layers

Author: [Your Name]
Created: [Original Date]
Updated: [Last Update]
Version: 1.0.0
"""

from photoshop import Session
import os
from datetime import date
import sys
import json

# Configuration Constants for TESTING
ROOT_PRODUCTS_DIR = "C:/Users/balma/Documents/ecommerce/lady cosmica/automation_testing"
WATERMARK_FILE_PATH = "C:/Users/balma/Documents/ecommerce/lady cosmica/graphics-watermarks-backgrounds/Lady-Cosmica-Watermark.png"
TEMPLATE_PATH = "C:/Users/balma/Documents/ecommerce/lady cosmica/background listing templates/1200X1200-blank-printify.png"

# Error Logging Setup
ERROR_OUTPUT_LOG_DIR = os.path.join(os.getcwd(), "Photoshop_scripts/Error_Log_Dir")
ERROR_LOG_COL_HEADERS = 'PRODUCT MOCKUP FILE,TRY-BLOCK-ID,ERROR'
Current_date = date.today()
CURRENT_DATE_ERROR_LOG_FILENAME = os.path.join(ERROR_OUTPUT_LOG_DIR, f"{Current_date}-Error Log.csv")
CURRENT_DATE_ERROR_LOG = open(CURRENT_DATE_ERROR_LOG_FILENAME, 'w')
CURRENT_DATE_ERROR_LOG.write(ERROR_LOG_COL_HEADERS)

def write_error_to_log(mockup_img, blockID, error):
    """
    Writes error information to the error log file.

    Args:
        mockup_img (str): Name of the image file being processed
        blockID (str): Identifier for the code block where error occurred
        error (str): Error message or details

    Returns:
        None

    Notes:
        Errors are written in CSV format with columns:
        PRODUCT MOCKUP FILE, TRY-BLOCK-ID, ERROR
    """
    error_entry = f"{mockup_img},{blockID},{error}"
    CURRENT_DATE_ERROR_LOG.write(error_entry)

def movelayer(layerbounds, fx, fy):
    """
    Calculates the movement required to position a layer at specified coordinates.

    Args:
        layerbounds (tuple): Current layer boundaries (x1, y1, x2, y2)
        fx (float): Target x coordinate
        fy (float): Target y coordinate

    Returns:
        list: Movement deltas [-dx, -dy] required to reach target position

    Technical Note:
        Movement is calculated as the difference between target and current position.
        Negative values are used because Photoshop's coordinate system origin is top-left.
    """
    curr_x = layerbounds[0]
    curr_y = layerbounds[1]
    new_x = fx - curr_x
    new_y = fy - curr_y
    return [-new_x, -new_y]

def get_watermark_props():
    """
    Returns watermark properties from saved configuration.
    If no configuration exists, uses default values.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'watermark_config.json')
    try:
        with open(config_path, 'r') as f:
            settings = json.load(f)
            return {
                'size': [
                    settings['size']['width'],
                    settings['size']['height']
                ],
                'opacity': settings['opacity'],
                'position': [
                    settings['position']['x'],
                    settings['position']['y']
                ]
            }
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default values if no config found
        return {
            'size': [124.875, 125],
            'opacity': 22,
            'position': [0, 245]
        }

def process_image(ps, img_path, output_dir):
    """
    Processes a single image with watermark in Photoshop.
    Must be called within Photoshop Session context.

    Args:
        ps: Photoshop Session object
        img_path: Path to image file
        output_dir: Directory for processed images
    """
    try:
        # Import image section
        desc = ps.ActionDescriptor
        desc.putPath(ps.app.charIDToTypeID("null"), img_path)
        ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
        
        curr_img_layer_name = ps.active_document.activeLayer.name
        img_layer = ps.active_document.activeLayer

        # Watermark section
        # [Rest of your existing watermark processing code]

    except Exception as e:
        write_error_to_log(img_path, "process_image", str(e))

def main():
    """Main execution function that processes images with Photoshop."""
    with Session(TEMPLATE_PATH, action="open") as ps:
        ps.app.preferences.rulerUnits = 1
        ps.app.displayDialogs = ps.DialogModes.DisplayErrorDialogs

        watermarked_img_output_dir = os.path.join(ROOT_PRODUCTS_DIR, "watermarked-output")
        if not os.path.exists(watermarked_img_output_dir):
            os.makedirs(watermarked_img_output_dir)

        for mockup_img in os.listdir(ROOT_PRODUCTS_DIR):
            if mockup_img == "watermarked-output":
                continue
                
            # [Your existing processing logic]

if __name__ == "__main__":
    main()