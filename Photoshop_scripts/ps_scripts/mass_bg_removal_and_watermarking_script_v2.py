"""
Mass Background Removal and Watermarking Script V2
------------------------------------------------
This script processes multiple product images by:
1. Removing backgrounds
2. Placing images on a template
3. Adding watermarks
4. Saving the processed images

The script processes all product folders in a root directory, creating
a 'watermarked_output' folder for each product's processed images.
"""

import os
from datetime import date
import time
from photoshop import Session
from typing import Dict, List, Tuple, Optional, Union
import sys

# Configuration
class Config:
    """Central configuration for the script"""
    
    def __init__(self, root_dir: str = None):
        self.ROOT_PRODUCTS_DIR = root_dir or "C:/Users/balma/Documents/ecommerce/lady cosmica/automation_testing_2"
        self.WATERMARK_FILE_PATH = "C:/Users/balma/Documents/ecommerce/lady cosmica/graphics-watermarks-backgrounds/Lady-Cosmica-Watermark.png"
        self.TEMPLATE_PATH = "C:/Users/balma/Documents/ecommerce/lady cosmica/background listing templates/base-template.png"
        
        # Error logging setup
        self.ERROR_OUTPUT_LOG_DIR = os.path.join(os.getcwd(), "Photoshop_scripts/Error_Log_Dir")
        self.ERROR_LOG_COL_HEADERS = 'PRODUCT MOCKUP FILE,TRY-BLOCK-ID,ERROR\n'
        self.current_date = date.today()
        self.ERROR_LOG_PATH = os.path.join(
            self.ERROR_OUTPUT_LOG_DIR,
            f"{self.current_date}-Error Log.csv"
        )

class ImagePresets:
    """Manages image placement presets for different contexts"""
    
    @staticmethod
    def get_preset(context: str) -> Optional[Dict]:
        """
        Get preset values for a specific image context.
        
        Args:
            context: Image context (e.g., 'front', 'context-1-front')
            
        Returns:
            Dictionary with preset values or None if context not found
        """
        presets = {
            'context-1-front': {
                'position': [612, 34],
                'rotate': 0,
                'size': [121.08, 121.08],
                'opacity': 100,
            },
            'context-2-front': {
                'position': [574, 77],
                'rotate': 0,
                'size': [124.75, 116.625],
                'opacity': 100,
            },
            'front': {
                'position': [404, -31],
                'rotate': 2.28,
                'size': [124.875, 125],
                'opacity': 100,
            }
        }
        return presets.get(context)

class ErrorLogger:
    """Handles error logging functionality"""
    
    def __init__(self, config: Config):
        self.config = config
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self):
        """Ensure error log file exists with headers"""
        if not os.path.exists(self.config.ERROR_OUTPUT_LOG_DIR):
            os.makedirs(self.config.ERROR_OUTPUT_LOG_DIR)
            
        if not os.path.isfile(self.config.ERROR_LOG_PATH):
            with open(self.config.ERROR_LOG_PATH, 'w') as f:
                f.write(self.config.ERROR_LOG_COL_HEADERS)
    
    def log_error(self, mockup_img: str, block_id: str, error: str):
        """Log an error to the error log file"""
        with open(self.config.ERROR_LOG_PATH, 'a') as f:
            error_entry = f"{mockup_img},{block_id},{error}\n"
            f.write(error_entry)

class ImageProcessor:
    """Handles image processing operations"""
    
    def __init__(self, config: Config, logger: ErrorLogger):
        self.config = config
        self.logger = logger
    
    @staticmethod
    def calculate_position_deltas(layer_bounds: List[float], target_x: float, target_y: float) -> Tuple[float, float]:
        """
        Calculate position deltas for image translation
        
        Args:
            layer_bounds: Current layer bounds [x1, y1, x2, y2]
            target_x: Target X position
            target_y: Target Y position
            
        Returns:
            Tuple of (delta_x, delta_y)
        """
        curr_x = layer_bounds[0]
        curr_y = layer_bounds[1]
        
        delta_x = target_x - curr_x
        delta_y = target_y - curr_y
        
        return delta_x, delta_y
    
    @staticmethod
    def extract_context(filename: str) -> str:
        """Extract context from filename"""
        try:
            return filename[filename.find('label=')+6:-4]
        except:
            return ""
    
    def process_image(self, ps: Session, image_path: str, output_dir: str):
        """Process a single image"""
        try:
            # Import image
            desc = ps.ActionDescriptor
            desc.putPath(ps.app.charIDToTypeID("null"), image_path)
            ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
            time.sleep(1.5)
            
            # Get image context and presets
            context = self.extract_context(os.path.basename(image_path))
            preset = ImagePresets.get_preset(context)
            
            if not preset:
                self.logger.log_error(image_path, "PRESET", "No matching preset found")
                return
                
            # Apply presets
            img_layer = ps.active_document.activeLayer
            
            # Resize
            img_layer.resize(preset['size'][0], preset['size'][1])
            
            # Position
            bounds = img_layer.bounds
            dx, dy = self.calculate_position_deltas(bounds, *preset['position'])
            img_layer.translate(dx, dy)
            
            # Rotate
            if preset['rotate']:
                img_layer.rotate(preset['rotate'])
                
            # Set opacity
            img_layer.opacity = preset['opacity']
            
            # Save
            output_path = os.path.join(output_dir, f"{os.path.basename(image_path)}-edit")
            options = ps.JPEGSaveOptions(quality=5)
            ps.active_document.saveAs(output_path, options, asCopy=True)
            
            # Cleanup
            img_layer.remove()
            
        except Exception as e:
            self.logger.log_error(image_path, "PROCESSING", str(e))

def main():
    # Get root directory from command line if provided
    root_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Initialize
    config = Config(root_dir)
    logger = ErrorLogger(config)
    processor = ImageProcessor(config, logger)
    
    # Process images
    with Session(config.TEMPLATE_PATH, action="open") as ps:
        ps.app.displayDialogs = ps.DialogModes.DisplayNoDialogs
        
        for root, dirs, files in os.walk(config.ROOT_PRODUCTS_DIR):
            # Create output directory
            output_dir = os.path.join(root, "watermarked_output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Process each image
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(root, file)
                    processor.process_image(ps, image_path, output_dir)

if __name__ == "__main__":
    main() 