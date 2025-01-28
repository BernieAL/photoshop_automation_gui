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
    def __init__(self, template_path: str, watermark_path: str = None, settings_path: str = None):
        self.template_path = template_path
        self.watermark_path = watermark_path
        self.settings_path = settings_path or os.path.join(
            os.getcwd(), 
            "Photoshop_scripts/settings/context_placements.json"
        )
        self._ensure_settings_file()
        self.current_settings = None  # Store current unconfirmed settings
        
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
    
    def _calculate_size_percentage(self, initial_bounds, final_bounds) -> Tuple[float, float]:
        """
        Calculate size as percentage of original
        
        Args:
            initial_bounds: Initial layer bounds [left, top, right, bottom]
            final_bounds: Final layer bounds [left, top, right, bottom]
            
        Returns:
            Tuple of (width_percentage, height_percentage)
        """
        initial_width = initial_bounds[2] - initial_bounds[0]
        initial_height = initial_bounds[3] - initial_bounds[1]
        
        final_width = final_bounds[2] - final_bounds[0]
        final_height = final_bounds[3] - final_bounds[1]
        
        width_percentage = (final_width / initial_width) * 100
        height_percentage = (final_height / initial_height) * 100
        
        return [width_percentage, height_percentage]
    
    def set_placement_interactively(self, image_path: str, context: str) -> None:
        """
        Open Photoshop to set placement settings interactively
        
        Args:
            image_path: Path to the sample image
            context: Context identifier (e.g., 'front', 'back')
        """
        # Validate paths
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Sample image not found: {image_path}")
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
            
        # Normalize paths for Windows
        image_path = os.path.normpath(image_path)
        template_path = os.path.normpath(self.template_path)
        
        try:
            with Session(self.template_path, action="open") as ps:
                ps.app.displayDialogs = ps.DialogModes.DisplayNoDialogs
                
                # 1. Import image and remove background
                desc = ps.ActionDescriptor
                desc.putPath(ps.app.charIDToTypeID("null"), image_path)
                ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                time.sleep(1.5)  # Wait for import
                
                # Get the imported layer
                if len(ps.active_document.artLayers) < 2:
                    raise Exception("Failed to import image layer")
                    
                img_layer = ps.active_document.artLayers[0]
                
                # Remove background
                ps.app.doAction("remove_bg", "Default Actions")
                time.sleep(1.5)  # Wait for background removal
                
                # Store initial state after background removal
                initial_bounds = img_layer.bounds
                
                # Keep Photoshop open for user interaction
                # Settings will be captured when confirm_placement is called
                self.current_settings = {
                    'layer': img_layer,
                    'initial_bounds': initial_bounds,
                    'ps_session': ps,
                    'has_watermark': False  # Track if watermark has been added
                }
                
        except Exception as e:
            print(f"Error in set_placement_interactively: {str(e)}")
            print(f"Full error details: {repr(e)}")
            print(f"Image path: {image_path}")
            print(f"Template path: {self.template_path}")
            self.current_settings = None
            raise
    
    def confirm_placement(self) -> Dict:
        """
        Confirm the current placement and return settings
        
        Returns:
            Dict containing placement settings
        """
        if not self.current_settings:
            raise Exception("No active placement session")
            
        try:
            img_layer = self.current_settings['layer']
            initial_bounds = self.current_settings['initial_bounds']
            ps = self.current_settings['ps_session']
            settings = None
            
            try:
                # Try to get final state
                final_bounds = img_layer.bounds
                final_opacity = img_layer.opacity
                
                # Calculate settings
                settings = {
                    'size': [100, 100],  # 100% means no resize
                    'position': [final_bounds[0], final_bounds[1]],
                    'opacity': final_opacity
                }
                
                # Only calculate size percentages if bounds are different
                if final_bounds != initial_bounds:
                    settings['size'] = self._calculate_size_percentage(initial_bounds, final_bounds)
                
                # If watermark hasn't been added yet, add it now
                if not self.current_settings.get('has_watermark'):
                    if not self.watermark_path or not os.path.exists(self.watermark_path):
                        raise Exception("No valid watermark path provided")
                        
                    # Add watermark
                    desc = ps.ActionDescriptor
                    desc.putPath(ps.app.charIDToTypeID("null"), self.watermark_path)
                    ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                    time.sleep(1.5)
                    
                    watermark_layer = ps.active_document.artLayers[0]
                    watermark_layer.opacity = 50
                    
                    # Store that we've added the watermark
                    self.current_settings['has_watermark'] = True
                    
                    # Return without cleaning up so user can position watermark
                    return settings
                
            except Exception as e:
                print(f"Warning: Could not get layer properties, using initial values: {str(e)}")
                # If we can't get the final state, use initial values
                settings = {
                    'size': [100, 100],
                    'position': [initial_bounds[0], initial_bounds[1]],
                    'opacity': 100
                }
            
            # Store settings before cleanup
            final_settings = settings
            
            # Only do cleanup on final confirmation (after watermark)
            if self.current_settings.get('has_watermark'):
                try:
                    if ps and ps.active_document:
                        # Remove both image and watermark layers
                        while len(ps.active_document.artLayers) > 1:  # Keep template layer
                            ps.active_document.artLayers[0].remove()
                except Exception as e:
                    print(f"Warning: Non-critical error during cleanup: {str(e)}")
                
                # Clear current settings only after watermark is done
                self.current_settings = None
            
            return final_settings
            
        except Exception as e:
            print(f"Error confirming placement: {str(e)}")
            self.current_settings = None
            raise
    
    def has_active_session(self) -> bool:
        """Check if there's an active placement session"""
        return self.current_settings is not None 