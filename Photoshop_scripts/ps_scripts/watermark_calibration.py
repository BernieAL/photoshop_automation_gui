#!/usr/bin/env python3
"""
Watermark Calibration Script

This script allows users to visually position a watermark on their own sample image
and saves those settings for batch processing. Designed for Etsy listing photos
and Printify mockups.

Process:
1. User selects a sample mockup image
2. User selects watermark image
3. Both are opened in Photoshop
4. User positions watermark manually
5. Settings are captured and saved for batch processing
"""

from photoshop import Session
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def get_image_paths():
    """
    Opens file dialogs for user to select sample image and watermark.
    
    Returns:
        tuple: (sample_image_path, watermark_path) or (None, None) if cancelled
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Get sample image
    print("\nSelect a sample mockup image (preferably one that represents your typical listing photo)...")
    sample_image = filedialog.askopenfilename(
        title="Select Sample Image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png"),
            ("All files", "*.*")
        ]
    )
    
    if not sample_image:
        print("No sample image selected. Exiting...")
        return None, None

    # Get watermark image
    print("\nSelect your watermark image...")
    watermark = filedialog.askopenfilename(
        title="Select Watermark Image",
        filetypes=[
            ("PNG files", "*.png"),  # Preferably PNG for transparency
            ("Image files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
    )
    
    if not watermark:
        print("No watermark selected. Exiting...")
        return None, None

    return sample_image, watermark

def capture_watermark_settings(ps, watermark_layer):
    """
    Captures current watermark layer settings including position, size, and opacity.
    """
    bounds = watermark_layer.bounds
    
    # Get current dimensions
    current_width = bounds[2] - bounds[0]  # right - left
    current_height = bounds[3] - bounds[1]  # bottom - top
    
    # Get document dimensions directly (they're already floats)
    original_width = ps.active_document.width
    original_height = ps.active_document.height
    
    # Calculate size percentages
    width_percentage = (current_width / original_width) * 100
    height_percentage = (current_height / original_height) * 100
    
    settings = {
        'size': {
            'width': width_percentage,
            'height': height_percentage
        },
        'position': {
            'x': bounds[0],
            'y': bounds[1]
        },
        'opacity': watermark_layer.opacity,
        'original_dimensions': {
            'width': original_width,
            'height': original_height
        }
    }
    
    # Debug info
    print(f"Debug Info:")
    print(f"Bounds: {bounds}")
    print(f"Document dimensions: {original_width} x {original_height}")
    print(f"Current dimensions: {current_width} x {current_height}")
    print(f"Calculated percentages: {width_percentage}% x {height_percentage}%")
    
    return settings

def save_settings(settings, config_file='watermark_config.json'):
    """Saves watermark settings to config file"""
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_path, 'w') as f:
        json.dump(settings, f, indent=4)
    
    # Show success message
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Success",
        "Watermark settings have been saved!\n\n"
        "You can now use the batch watermark script to process multiple images."
    )

def main():
    # Get image paths from user
    sample_image, watermark = get_image_paths()
    if not sample_image or not watermark:
        return

    try:
        with Session() as ps:
            # Open sample image
            doc = ps.app.open(sample_image)
            
            # Place watermark
            desc = ps.ActionDescriptor
            desc.putPath(ps.app.charIDToTypeID("null"), watermark)
            ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
            
            watermark_layer = ps.active_document.activeLayer
            
            # First dialog - Position and Size
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "Watermark Calibration - Step 1",
                "Position and Size Your Watermark:\n\n"
                "1. Move the watermark to desired position\n"
                "2. Use Ctrl/Cmd+T to resize if needed\n"
                "3. Press ENTER to apply transform\n\n"
                "Click OK when ready for opacity adjustment."
            )

            # Second dialog - Opacity
            messagebox.showinfo(
                "Watermark Calibration - Step 2",
                "Adjust Watermark Opacity:\n\n"
                "1. In Photoshop's Layers panel, find 'Opacity' at the top\n"
                "2. Click the opacity value (currently 100%)\n"
                "3. Type or slide to adjust opacity\n"
                "   - Recommended: Try 20-40% for watermarks\n"
                "   - Test visibility against both light and dark areas\n\n"
                "Click OK when you're satisfied with the opacity."
            )
            
            # Final confirmation
            if not messagebox.askyesno(
                "Save Settings",
                "Are you happy with the watermark position, size, and opacity?\n\n"
                "Click Yes to save these settings\n"
                "Click No to cancel and try again"
            ):
                ps.active_document.close(ps.SaveOptions.DoNotSaveChanges)
                return
            
            # Capture and save settings
            settings = capture_watermark_settings(ps, watermark_layer)
            save_settings(settings)
            
            # Clean up
            ps.active_document.close(ps.SaveOptions.DoNotSaveChanges)
            
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error",
            f"An error occurred during calibration:\n{str(e)}\n\n"
            "Please make sure Photoshop is running and try again."
        )
        raise  # This will show the full error in the console for debugging

if __name__ == "__main__":
    main() 