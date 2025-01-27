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
    
    def process_images(self, 
                      folder: str, 
                      is_mass_mode: bool,
                      operations: Set[str],
                      context_settings: Dict,
                      status_callback=None):
        """
        Process images in the folder based on selected operations.
        
        Args:
            folder: Root folder containing images
            is_mass_mode: Whether to process all subfolders
            operations: Set of operations to perform
            context_settings: Placement settings for each context
            status_callback: Optional callback for status updates
        """
        def log(msg: str):
            if status_callback:
                status_callback(msg)
            print(msg)
            
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
                    
                    img_layer = ps.active_document.activeLayer
                    
                    # Apply operations
                    if "Remove Background" in operations:
                        log(f"Removing background from {file}")
                        ps.app.doAction("remove_bg", "Default Actions")
                    
                    if "Custom Placement & Background" in operations:
                        # Get context and apply placement settings
                        context = self._extract_context(file)
                        if context and context in context_settings:
                            settings = context_settings[context]
                            log(f"Applying placement settings for context: {context}")
                            
                            # Apply settings
                            img_layer.resize(settings['size'][0], settings['size'][1])
                            img_layer.translate(settings['position'][0], settings['position'][1])
                            if settings.get('rotate'):
                                img_layer.rotate(settings['rotate'])
                            img_layer.opacity = settings['opacity']
                    
                    if "Add Watermark" in operations:
                        log(f"Adding watermark to {file}")
                        # Import watermark
                        desc = ps.ActionDescriptor
                        desc.putPath(ps.app.charIDToTypeID("null"), self.watermark_path)
                        ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                        time.sleep(1.5)
                        
                        # Position watermark (using default settings for now)
                        watermark_layer = ps.active_document.activeLayer
                        watermark_layer.opacity = 50
                    
                    # Save processed image
                    output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}-processed.jpg")
                    options = ps.JPEGSaveOptions(quality=12)
                    ps.active_document.saveAs(output_path, options, asCopy=True)
                    
                    # Clean up layers
                    while len(ps.active_document.artLayers) > 0:
                        ps.active_document.artLayers[0].remove()
                    
                except Exception as e:
                    log(f"Error processing {file}: {str(e)}")
                    continue
    
    def _extract_context(self, filename: str) -> Optional[str]:
        """Extract context from filename"""
        try:
            return filename[filename.find('label=')+6:-4]
        except:
            return None 