"""
Image Processor
-------------
Handles the actual processing of images including:
- Background removal
- Watermarking
- Custom placement
"""

import os
from photoshop import Session
import time
from typing import Set, Dict, Optional

class ImageProcessor:
    def __init__(self, template_path: str, watermark_path: str):
        self.template_path = template_path
        self.watermark_path = watermark_path
        self.watermark_settings = None
    
    def capture_watermark_settings(self, status_callback=None):
        """
        Opens Photoshop to let user position watermark and captures those settings.
        Returns True if settings were successfully captured.
        """
        def log(msg: str):
            if status_callback:
                status_callback(msg)
            print(msg)

        try:
            with Session(self.template_path, action="open") as ps:
                ps.app.displayDialogs = ps.DialogModes.DisplayNoDialogs
                
                # Place the watermark
                desc = ps.ActionDescriptor
                desc.putPath(ps.app.charIDToTypeID("null"), self.watermark_path)
                ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                time.sleep(1)
                
                # Get the watermark layer
                watermark_layer = ps.active_document.artLayers[0]
                watermark_layer.name = "Lady-Cosmica-Watermark"
                
                # Display instructions
                log("\nPosition the watermark:")
                log("1. Move and resize the watermark as desired")
                log("2. Adjust opacity in the Layers panel")
                log("3. When done, press Enter or click the checkmark (✓)")
                log("4. Then close Photoshop to save these settings")
                
                # Wait for user to position watermark
                input("\nPress Enter after positioning watermark in Photoshop...")
                
                # Capture the settings
                bounds = watermark_layer.bounds
                self.watermark_settings = {
                    'size': [bounds[2] - bounds[0], bounds[3] - bounds[1]],  # width, height
                    'position': [bounds[0], bounds[1]],  # x, y position
                    'opacity': watermark_layer.opacity
                }
                
                log("\nWatermark settings captured successfully!")
                log(f"Position: {self.watermark_settings['position']}")
                log(f"Size: {self.watermark_settings['size']}")
                log(f"Opacity: {self.watermark_settings['opacity']}%")
                
                return True
                
        except Exception as e:
            log(f"Error capturing watermark settings: {str(e)}")
            return False
    
    def set_watermark_settings(self, settings: Dict):
        """Set the watermark position settings to use for all images"""
        self.watermark_settings = settings
    
    def process_images(self, 
                      folder: str, 
                      is_mass_mode: bool,
                      operations: Set[str],
                      context_settings: Dict,
                      status_callback=None):
        """Process images in the folder based on selected operations."""
        def log(msg: str):
            if status_callback:
                status_callback(msg)
            print(msg)
        
        def apply_watermark(context_watermark_settings=None):
            """
            Helper function to consistently apply watermark settings.
            Uses context-specific settings if provided, otherwise uses default settings.
            """
            try:
                settings = context_watermark_settings or self.watermark_settings
                if not settings:
                    raise ValueError("No watermark settings available")
                
                # Debug log the settings
                log(f"DEBUG: Using watermark settings: {settings}")
                
                # Place the watermark
                desc = ps.ActionDescriptor
                desc.putPath(ps.app.charIDToTypeID("null"), self.watermark_path)
                ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                time.sleep(1)
                
                # Get the watermark layer
                watermark_layer = ps.active_document.artLayers[0]
                watermark_layer.name = "Lady-Cosmica-Watermark"
                
                # Get current dimensions
                current_bounds = watermark_layer.bounds
                current_width = current_bounds[2] - current_bounds[0]
                current_height = current_bounds[3] - current_bounds[1]
                
                # Debug log the current dimensions
                log(f"DEBUG: Current watermark dimensions: {current_width} x {current_height}")
                
                # Get target dimensions from settings
                if isinstance(settings, dict) and 'watermark' in settings:
                    # If settings come from context_settings
                    watermark_settings = settings['watermark']
                else:
                    # If settings are direct watermark settings
                    watermark_settings = settings
                
                # Get target dimensions (handle both 'dimensions' and 'size' keys for compatibility)
                target_dimensions = watermark_settings.get('dimensions') or watermark_settings.get('size')
                if not target_dimensions:
                    raise ValueError("No size/dimensions found in watermark settings")
                    
                target_width, target_height = target_dimensions
                
                # Debug log the target dimensions
                log(f"DEBUG: Target dimensions: {target_width} x {target_height}")
                
                # Calculate resize percentages
                width_scale = (target_width / current_width) * 100
                height_scale = (target_height / current_height) * 100
                
                # Debug log the scale factors
                log(f"DEBUG: Scale factors: {width_scale}% x {height_scale}%")
                
                # Resize to match original dimensions
                watermark_layer.resize(width_scale, height_scale)
                time.sleep(0.5)
                
                # Move to captured position
                current_bounds = watermark_layer.bounds
                x_move = watermark_settings['position'][0] - current_bounds[0]
                y_move = watermark_settings['position'][1] - current_bounds[1]
                
                # Debug log the movement
                log(f"DEBUG: Moving by: {x_move}, {y_move}")
                
                watermark_layer.translate(x_move, y_move)
                
                # Set opacity
                watermark_layer.opacity = watermark_settings['opacity']
                
            except Exception as e:
                log(f"DEBUG: Full settings object: {settings}")
                log(f"DEBUG: Error type: {type(e)}")
                log(f"DEBUG: Error details: {str(e)}")
                raise ValueError(f"Failed to apply watermark settings: {str(e)}")
        
        def cleanup_layers(keep_template=True):
            """Helper function to consistently clean up layers"""
            min_layers = 1 if keep_template else 0
            while len(ps.active_document.artLayers) > min_layers:
                ps.active_document.artLayers[0].remove()
                time.sleep(0.5)
        
        # Verify watermark settings if needed
        needs_watermark = ("Add Watermark ONLY" in operations or 
                         "Custom Placement + Background Removal + Watermark" in operations)
        
        if needs_watermark and not self.watermark_settings and not context_settings:
            raise ValueError("No watermark settings provided")
            
        with Session(self.template_path, action="open") as ps:
            ps.app.displayDialogs = ps.DialogModes.DisplayNoDialogs
            
            # Get list of files to process
            files_to_process = []
            if is_mass_mode:
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            files_to_process.append((root, file))
            else:
                for file in os.listdir(folder):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        files_to_process.append((folder, file))
            
            total_files = len(files_to_process)
            log(f"Found {total_files} images to process")
            
            # Process each file
            for i, (root, file) in enumerate(files_to_process, 1):
                try:
                    log(f"Processing {i}/{total_files}: {file}")
                    
                    # Create output directory if needed
                    output_dir = os.path.join(root, "processed_output")
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    # Import image
                    image_path = os.path.join(root, file)
                    desc = ps.ActionDescriptor
                    desc.putPath(ps.app.charIDToTypeID("null"), image_path)
                    ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                    time.sleep(1.5)
                    
                    # Get the image layer
                    img_layer = ps.active_document.artLayers[0]
                    
                    # Get context from filename
                    context = self._extract_context(file)
                    context_settings_for_image = context_settings.get(context) if context else None
                    
                    if "Remove Background ONLY" in operations or "Custom Placement + Background Removal + Watermark" in operations:
                        # Remove background
                        log(f"Removing background from {file}")
                        ps.app.doAction("remove_bg", "Default Actions")
                    
                    if needs_watermark:
                        # Use context-specific watermark settings if available
                        if context_settings_for_image and 'watermark' in context_settings_for_image:
                            apply_watermark(context_settings_for_image['watermark'])
                        else:
                            apply_watermark()
                    
                    # Save processed image
                    output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}-processed.jpg")
                    options = ps.JPEGSaveOptions(quality=12)
                    ps.active_document.saveAs(output_path, options, asCopy=True)
                    
                    # Clean up layers before next image
                    cleanup_layers()
                    
                except Exception as e:
                    log(f"Error processing {file}: {str(e)}")
                    # Clean up any remaining layers
                    try:
                        cleanup_layers()
                    except:
                        pass
                    continue
    
    def _extract_context(self, filename: str) -> Optional[str]:
        """Extract context from filename"""
        try:
            return filename[filename.find('label=')+6:-4]
        except:
            return None 