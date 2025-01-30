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
        self.current_image_path = None  # Store path of current image being processed
        
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
        # Add delay before starting new session
        time.sleep(2)
        
        # Store current image path
        self.current_image_path = image_path
        
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
                
                # Display guidance about committing transformations
                print("\nIMPORTANT: If you resize or rotate the image:")
                print("- Click the checkmark (✓) in Photoshop")
                print("- Or press Enter")
                print("- Or click outside the transform box")
                print("This commits your changes before proceeding.\n")
                
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
            # Add delay on error
            time.sleep(2)
            raise
    
    def confirm_placement(self) -> Dict:
        """
        Confirm the current placement and return settings
        
        Returns:
            Dict containing placement settings
        """
        if not self.current_settings:
            raise Exception("No active session to save")
            
        try:
            img_layer = self.current_settings['layer']
            initial_bounds = self.current_settings['initial_bounds']
            ps = self.current_settings['ps_session']
            settings = None
            
            # Function to try committing placement
            def try_commit_placement():
                try:
                    # Simulate Enter key press to commit placement
                    ps.app.doJavaScript('app.sendKeyboardShortcut("Enter");')
                    time.sleep(1)  # Wait for commit to process
                    return True
                except Exception as e:
                    print(f"Failed to commit placement: {str(e)}")
                    return False
            
            # Function to attempt reconnection
            def try_reconnect(max_attempts=3):
                for attempt in range(max_attempts):
                    try:
                        print(f"\nReconnection attempt {attempt + 1} of {max_attempts}...")
                        time.sleep(2)  # Wait before reconnecting
                        
                        # Create new session
                        new_ps = Session(self.template_path, action="open")
                        new_ps.app.displayDialogs = new_ps.DialogModes.DisplayNoDialogs
                        
                        # Verify we can access the document
                        if new_ps.active_document and new_ps.active_document.artLayers.length > 0:
                            print("Successfully reconnected to Photoshop")
                            return new_ps, new_ps.active_document.artLayers[0]
                    except Exception as e:
                        print(f"Reconnection attempt {attempt + 1} failed: {str(e)}")
                        if attempt < max_attempts - 1:
                            print("Waiting before next attempt...")
                            time.sleep(3)  # Longer wait between attempts
                
                return None, None
            
            # Verify Photoshop connection is still active
            try:
                # Test connection by accessing a simple property
                _ = ps.active_document.artLayers.length
            except Exception as e:
                print(f"Lost connection to Photoshop: {str(e)}")
                # Check if it's due to uncommitted placement
                if "Please check if you have Photoshop installed correctly" in str(e):
                    print("\nDetected uncommitted transformation!")
                    print("Since you resized or rotated the element, you need to commit the changes:")
                    print("1. Click the checkmark (✓) in Photoshop")
                    print("2. Or press Enter")
                    print("3. Or click outside the transform box")
                    
                    if try_commit_placement():
                        print("Successfully committed transformation")
                        # Re-get the layer reference
                        img_layer = ps.active_document.artLayers[0]
                        self.current_settings['layer'] = img_layer
                    else:
                        # Try to reconnect
                        print("\nAttempting to recover from uncommitted state...")
                        new_ps, new_layer = try_reconnect()
                        if new_ps and new_layer:
                            ps = new_ps
                            img_layer = new_layer
                            self.current_settings['ps_session'] = ps
                            self.current_settings['layer'] = img_layer
                        else:
                            print("\nFailed to recover session")
                            print("Please try the following:")
                            print("1. Check if Photoshop is responding")
                            print("2. Make sure to commit any transformations (click ✓ or press Enter)")
                            print("3. Try the operation again")
                            raise Exception("Unable to recover Photoshop session")
                else:
                    # Try to reconnect for other connection issues
                    print("\nAttempting to reconnect to Photoshop...")
                    new_ps, new_layer = try_reconnect()
                    if new_ps and new_layer:
                        ps = new_ps
                        img_layer = new_layer
                        self.current_settings['ps_session'] = ps
                        self.current_settings['layer'] = img_layer
                    else:
                        print("\nFailed to reconnect to Photoshop")
                        print("Please try the following:")
                        print("1. Check if Photoshop is running")
                        print("2. Make sure no dialog boxes are open")
                        print("3. Try the operation again")
                        raise Exception("Unable to reconnect to Photoshop")
            
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
                    
                    print("\nAdding watermark...")
                    print("IMPORTANT: If you resize or rotate the watermark:")
                    print("- Click the checkmark (✓) in Photoshop")
                    print("- Or press Enter")
                    print("- Or click outside the transform box")
                    print("This commits your changes before proceeding.\n")
                    
                    # Add watermark with retry logic
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            desc = ps.ActionDescriptor
                            desc.putPath(ps.app.charIDToTypeID("null"), self.watermark_path)
                            ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                            time.sleep(1.5)
                            
                            watermark_layer = ps.active_document.artLayers[0]
                            watermark_layer.opacity = 50
                            
                            # Store that we've added the watermark
                            self.current_settings['has_watermark'] = True
                            print("Watermark added successfully")
                            print("Position the watermark as desired")
                            print("Remember to commit if you resize or rotate!")
                            break
                        except Exception as e:
                            print(f"Attempt {attempt + 1} failed: {str(e)}")
                            # Check if it's due to uncommitted placement
                            if "Please check if you have Photoshop installed correctly" in str(e):
                                print("Detected uncommitted placement, attempting to commit...")
                                if try_commit_placement():
                                    print("Successfully committed placement")
                                    continue
                            if attempt < max_retries - 1:
                                print("Retrying watermark placement...")
                                time.sleep(2)  # Wait before retry
                            else:
                                raise Exception("Failed to add watermark after multiple attempts")
                    
                    # Return without cleaning up so user can position watermark
                    return settings
                
            except Exception as e:
                print(f"Warning during layer property access: {str(e)}")
                # If we can't get the final state, use initial values
                settings = {
                    'size': [100, 100],
                    'position': [initial_bounds[0], initial_bounds[1]],
                    'opacity': 100
                }
            
            # Store settings before cleanup
            final_settings = settings
            
            # Only do cleanup and save on final confirmation (after watermark)
            if self.current_settings.get('has_watermark'):
                try:
                    print("Starting final save process...")  # Debug print
                    
                    if not self.current_image_path:
                        raise Exception("No current image path available")
                    
                    # Create output directory and prepare path
                    output_dir = os.path.join(os.path.dirname(self.current_image_path), "processed_output")
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(self.current_image_path))[0]}-processed.jpg")
                    
                    print(f"Saving to: {output_path}")  # Debug print
                    
                    # Save with retry logic
                    max_save_retries = 3
                    for save_attempt in range(max_save_retries):
                        try:
                            options = ps.JPEGSaveOptions(quality=12)
                            ps.active_document.saveAs(output_path, options, asCopy=True)
                            time.sleep(1.5)  # Wait for save to complete
                            print("Save completed successfully")  # Debug print
                            break
                        except Exception as save_error:
                            print(f"Save attempt {save_attempt + 1} failed: {str(save_error)}")
                            if save_attempt < max_save_retries - 1:
                                print("Retrying save...")
                                time.sleep(2)  # Wait before retry
                            else:
                                raise Exception("Failed to save after multiple attempts")
                    
                    # Store output path in settings for UI feedback
                    final_settings['output_path'] = output_path
                    
                    print("Cleaning up layers...")  # Debug print
                    
                    # Remove layers with retry logic
                    cleanup_retries = 3
                    for cleanup_attempt in range(cleanup_retries):
                        try:
                            while len(ps.active_document.artLayers) > 1:  # Keep template layer
                                ps.active_document.artLayers[0].remove()
                                time.sleep(0.5)  # Small delay between layer removals
                            print("Cleanup completed")  # Debug print
                            break
                        except Exception as cleanup_error:
                            print(f"Cleanup attempt {cleanup_attempt + 1} failed: {str(cleanup_error)}")
                            if cleanup_attempt < cleanup_retries - 1:
                                print("Retrying cleanup...")
                                time.sleep(2)  # Wait before retry
                            else:
                                print("Warning: Cleanup failed, but save was successful")
                    
                except Exception as e:
                    print(f"Error during save/cleanup: {str(e)}")
                    print(f"Current image path: {self.current_image_path}")
                    raise  # Re-raise the exception to handle it in the UI
                finally:
                    # Clear current settings only after everything is done
                    print("Clearing session state...")  # Debug print
                    self.current_settings = None
                    self.current_image_path = None
                    # Add delay before next operation
                    time.sleep(2)
            
            return final_settings
            
        except Exception as e:
            print(f"Error in confirm_placement: {str(e)}")
            # Don't clear settings on error unless it was the final confirmation
            if self.current_settings and self.current_settings.get('has_watermark'):
                print("Clearing session state due to error in final confirmation")  # Debug print
                self.current_settings = None
                self.current_image_path = None
                # Add delay on error too
                time.sleep(2)
            raise
    
    def has_active_session(self) -> bool:
        """Check if there's an active placement session"""
        return self.current_settings is not None 