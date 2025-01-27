"""
Context Placement Handler
-----------------------
Handles the interactive placement of images in Photoshop,
allowing users to set and save placement settings for each context.
"""

import os
import json
from photoshop import Session
import time
from typing import Dict, Optional, Tuple

class ContextPlacementHandler:
    def __init__(self, template_path: str, settings_path: str = None):
        self.template_path = template_path
        self.settings_path = settings_path or os.path.join(
            os.getcwd(), 
            "Photoshop_scripts/settings/context_placements.json"
        )
        self._ensure_settings_file()
        
    def _ensure_settings_file(self):
        """Ensure settings directory and file exist"""
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        if not os.path.exists(self.settings_path):
            with open(self.settings_path, 'w') as f:
                json.dump({}, f)
    
    def get_placement_settings(self, context: str) -> Optional[Dict]:
        """Get saved placement settings for a context"""
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
                return settings.get(context)
        except:
            return None
    
    def save_placement_settings(self, context: str, settings: Dict):
        """Save placement settings for a context"""
        try:
            with open(self.settings_path, 'r') as f:
                all_settings = json.load(f)
        except:
            all_settings = {}
            
        all_settings[context] = settings
        
        with open(self.settings_path, 'w') as f:
            json.dump(all_settings, f, indent=2)
    
    def capture_placement_settings(self, context: str, sample_image_path: str) -> Dict:
        """
        Open Photoshop with template and sample image to capture placement settings.
        Returns the captured settings.
        """
        with Session(self.template_path, action="open") as ps:
            ps.app.displayDialogs = ps.DialogModes.DisplayNoDialogs
            
            # Import sample image
            desc = ps.ActionDescriptor
            desc.putPath(ps.app.charIDToTypeID("null"), sample_image_path)
            ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
            time.sleep(1.5)
            
            # Get the active layer (the imported image)
            img_layer = ps.active_document.activeLayer
            
            # Display instructions
            instructions = (
                "1. Position and resize the image as desired\n"
                "2. When finished, press Enter to capture settings"
            )
            ps.app.doJavaScript(f'alert("{instructions}")')
            
            # Wait for user to position the image
            input("Press Enter when image is positioned...")
            
            # Capture settings
            settings = {
                'position': [img_layer.bounds[0], img_layer.bounds[1]],  # x, y position
                'size': self._calculate_size_percentage(img_layer),
                'rotate': img_layer.rotate if hasattr(img_layer, 'rotate') else 0,
                'opacity': img_layer.opacity
            }
            
            # Clean up
            img_layer.remove()
            
            return settings
    
    def _calculate_size_percentage(self, layer) -> Tuple[float, float]:
        """Calculate size as percentage of original"""
        bounds = layer.bounds
        current_width = bounds[2] - bounds[0]
        current_height = bounds[3] - bounds[1]
        
        # TODO: Need to store original dimensions somewhere or pass them in
        # For now, returning raw dimensions
        return [current_width, current_height]
    
    def set_placement_interactive(self, context: str, sample_image_path: str) -> Dict:
        """
        Main method to handle interactive placement setting.
        Opens Photoshop, lets user set placement, saves settings.
        """
        # Capture settings through Photoshop
        settings = self.capture_placement_settings(context, sample_image_path)
        
        # Save the settings
        self.save_placement_settings(context, settings)
        
        return settings 