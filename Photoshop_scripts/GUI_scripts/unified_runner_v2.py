"""
Unified Photoshop Automation Runner
---------------------------------
A GUI tool that allows users to:
1. Select single folder or mass folder processing
2. Choose which operations to perform (bg removal, watermarking, placement)
3. Interactively set placement settings for each image context
"""

import customtkinter as ctk
import os
from typing import Dict, Set
import json
from photoshop import Session
import time
from context_placement_handler import ContextPlacementHandler
from image_processor import ImageProcessor

class ProcessingOptions:
    """Stores the selected processing options"""
    REMOVE_BG = "Remove Background ONLY"
    ADD_WATERMARK = "Add Watermark ONLY"
    CUSTOM_PLACEMENT = "Custom Placement + Background Removal + Watermark"
    
    @staticmethod
    def get_all_options():
        return [
            ProcessingOptions.REMOVE_BG,
            ProcessingOptions.ADD_WATERMARK,
            ProcessingOptions.CUSTOM_PLACEMENT
        ]

class UnifiedRunnerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Photoshop Automation Runner")
        self.geometry("1000x800")
        self.minsize(1000, 800)  # Set minimum window size
        
        # State variables
        self.selected_folders = []
        self.processing_options = set()
        self.context_settings = {}  # Stores placement settings for each context
        
        # Initialize paths
        self.template_path = "C:/Users/balma/Documents/ecommerce/lady cosmica/background listing templates/base-template.png"  # TODO: Make configurable
        self.watermark_path = "C:/Users/balma/Documents/ecommerce/lady cosmica/graphics-watermarks-backgrounds/Lady-Cosmica-Watermark.png"  # TODO: Make configurable
        
        # Initialize handlers
        self.placement_handler = ContextPlacementHandler(
            template_path=self.template_path,
            watermark_path=self.watermark_path
        )
        self.image_processor = ImageProcessor(self.template_path, self.watermark_path)
        
        self._create_gui()
    
    def _create_gui(self):
        """Create the main GUI elements"""
        # Create outer scrollable container
        outer_frame = ctk.CTkFrame(self)
        outer_frame.pack(fill="both", expand=True)
        
        # Main scrollable container
        self.main_frame = ctk.CTkScrollableFrame(
            outer_frame,
            width=960,  # Slightly less than window width to avoid horizontal scroll
            height=780  # Slightly less than window height to avoid window resize
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configuration Section
        self._create_config_section()
        
        # Folder Selection Section
        self._create_folder_section()
        
        # Processing Options Section
        self._create_options_section()
        
        # Context Settings Section (initially hidden)
        self._create_context_settings_section()
        
        # Action Buttons
        self._create_action_buttons()
        
        # Status Display
        self._create_status_section()
    
    def _create_config_section(self):
        """Create the configuration section"""
        config_frame = ctk.CTkFrame(self.main_frame)
        config_frame.pack(fill="x", padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            config_frame,
            text="Configuration",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=5)
        
        # Watermark Path
        watermark_frame = ctk.CTkFrame(config_frame)
        watermark_frame.pack(fill="x", padx=5, pady=5)
        
        watermark_label = ctk.CTkLabel(watermark_frame, text="Watermark:")
        watermark_label.pack(side="left", padx=5)
        
        self.watermark_entry = ctk.CTkEntry(watermark_frame, width=400)
        self.watermark_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.watermark_entry.insert(0, self.watermark_path)
        
        watermark_browse = ctk.CTkButton(
            watermark_frame,
            text="Browse",
            command=self._browse_watermark,
            width=100
        )
        watermark_browse.pack(side="right", padx=5)
    
    def _create_folder_section(self):
        """Create the folder selection section"""
        folder_frame = ctk.CTkFrame(self.main_frame)
        folder_frame.pack(fill="x", padx=10, pady=5)
        
        # Folder selection mode
        mode_label = ctk.CTkLabel(folder_frame, text="Processing Mode:")
        mode_label.pack(side="left", padx=5)
        
        self.mode_var = ctk.StringVar(value="single")
        single_radio = ctk.CTkRadioButton(
            folder_frame, 
            text="Single Folder",
            variable=self.mode_var,
            value="single",
            command=self._on_mode_change
        )
        single_radio.pack(side="left", padx=5)
        
        mass_radio = ctk.CTkRadioButton(
            folder_frame, 
            text="Mass Processing",
            variable=self.mode_var,
            value="mass",
            command=self._on_mode_change
        )
        mass_radio.pack(side="left", padx=5)
        
        # Folder selection
        self.folder_entry = ctk.CTkEntry(folder_frame, width=400)
        self.folder_entry.pack(side="left", padx=5)
        
        browse_btn = ctk.CTkButton(
            folder_frame,
            text="Browse",
            command=self._browse_folder
        )
        browse_btn.pack(side="left", padx=5)
    
    def _create_options_section(self):
        """Create the processing options section"""
        options_frame = ctk.CTkFrame(self.main_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="Select Processing Options:",
            font=("Arial", 14, "bold")
        )
        options_label.pack(pady=5)
        
        # Checkboxes for each option
        self.option_vars = {}
        for option in ProcessingOptions.get_all_options():
            var = ctk.BooleanVar()
            self.option_vars[option] = var
            
            checkbox = ctk.CTkCheckBox(
                options_frame,
                text=option,
                variable=var,
                command=self._on_option_change
            )
            checkbox.pack(pady=2)
    
    def _create_context_settings_section(self):
        """Create the context settings section (initially hidden)"""
        self.context_frame = ctk.CTkFrame(self.main_frame)
        # Will be packed when needed
        
        self.context_label = ctk.CTkLabel(
            self.context_frame,
            text="Settings For Image Context(s)",
            font=("Arial", 14, "bold")
        )
        self.context_label.pack(pady=5)
        
        # Create scrollable frame for contexts
        self.context_scroll = ctk.CTkScrollableFrame(
            self.context_frame,
            height=250  # Fixed height
        )
        self.context_scroll.pack(fill="x", padx=5, pady=5)
        
        # Will be populated when contexts are detected
        self.context_widgets = {}
    
    def _create_action_buttons(self):
        """Create the action buttons"""
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.analyze_btn = ctk.CTkButton(
            button_frame,
            text="Analyze Folders",
            command=self._analyze_folders
        )
        self.analyze_btn.pack(side="left", padx=5)
        
        self.run_btn = ctk.CTkButton(
            button_frame,
            text="Run Processing",
            command=self._run_processing,
            state="disabled"
        )
        self.run_btn.pack(side="left", padx=5)
    
    def _create_status_section(self):
        """Create the status display section"""
        # Create a frame to hold both the status text and clear button
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        # Add clear button
        self.clear_btn = ctk.CTkButton(
            status_frame,
            text="Clear Output",
            command=self._clear_output,
            width=100
        )
        self.clear_btn.pack(side="bottom", pady=(5, 0))
        
        # Create scrollable text box
        self.status_text = ctk.CTkTextbox(
            status_frame,
            height=150,  # Reduced height
            width=600
        )
        self.status_text.pack(fill="x", padx=0, pady=(0, 5))
    
    def _browse_folder(self):
        """Handle folder browsing"""
        if self.mode_var.get() == "single":
            folder = ctk.filedialog.askdirectory()
            if folder:
                self.folder_entry.delete(0, 'end')
                self.folder_entry.insert(0, folder)
        else:
            folder = ctk.filedialog.askdirectory()
            if folder:
                self.folder_entry.delete(0, 'end')
                self.folder_entry.insert(0, folder)
    
    def _on_mode_change(self):
        """Handle processing mode change"""
        mode = self.mode_var.get()
        self.folder_entry.delete(0, 'end')
        
        if mode == "mass":
            self.status_text.insert('end', "Mass processing mode: Select root folder containing product folders\n")
        else:
            self.status_text.insert('end', "Single folder mode: Select folder containing images\n")
    
    def _on_option_change(self):
        """Handle processing option changes"""
        self.processing_options = {
            option for option, var in self.option_vars.items() 
            if var.get()
        }
        
        # Show/hide context settings based on options
        if ProcessingOptions.CUSTOM_PLACEMENT in self.processing_options:
            self.context_frame.pack(fill="x", padx=10, pady=10)
        else:
            self.context_frame.pack_forget()
    
    def _analyze_folders(self):
        """Analyze selected folders for image contexts"""
        folder = self.folder_entry.get()
        if not folder:
            self.status_text.insert('end', "Please select a folder first\n")
            return
            
        self.status_text.delete('1.0', 'end')
        self.status_text.insert('end', f"Analyzing folder: {folder}\n")
        
        # Find all unique contexts
        contexts = set()
        if self.mode_var.get() == "single":
            contexts = self._analyze_single_folder(folder)
        else:
            contexts = self._analyze_mass_folders(folder)
            
        if contexts:
            self.status_text.insert('end', f"Found contexts: {', '.join(contexts)}\n")
            self._setup_context_settings(contexts)
            self.run_btn.configure(state="normal")
        else:
            self.status_text.insert('end', "No image contexts found\n")
    
    def _analyze_single_folder(self, folder: str) -> Set[str]:
        """Analyze a single folder for image contexts"""
        contexts = set()
        for file in os.listdir(folder):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                context = self._extract_context(file)
                if context:
                    contexts.add(context)
        return contexts
    
    def _analyze_mass_folders(self, root_folder: str) -> Set[str]:
        """Analyze all folders under root for image contexts"""
        contexts = set()
        for root, _, files in os.walk(root_folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    context = self._extract_context(file)
                    if context:
                        contexts.add(context)
        return contexts
    
    def _extract_context(self, filename: str) -> str:
        """Extract context from filename"""
        try:
            return filename[filename.find('label=')+6:-4]
        except:
            return ""
    
    def _setup_context_settings(self, contexts: Set[str]):
        """Setup the context settings UI"""
        # Clear existing widgets
        for widget in self.context_widgets.values():
            widget.destroy()
        self.context_widgets.clear()
        
        # Add instructions at the top
        instructions_frame = ctk.CTkFrame(self.context_frame)
        instructions_frame.pack(fill="x", padx=5, pady=5)
        
        instructions_label = ctk.CTkLabel(
            instructions_frame,
            text=(
                "Placement Process for Each Context:\n"
                "1. Background will be removed automatically\n"
                "2. Position the image as desired\n"
                "3. Click 'Confirm Image Position'\n"
                "4. Position the watermark\n"
                "5. Click 'Confirm Watermark Position' to finish\n"
                "\nButton Color Guide:\n"
                "• Blue - Ready for image placement\n"
                "• Gold - Image placement confirmed, needs watermark\n"
                "• Green - Both image and watermark confirmed"
            ),
            justify="left"
        )
        instructions_label.pack(pady=5, padx=5)
        
        # Add Set All button
        set_all_frame = ctk.CTkFrame(self.context_frame)
        set_all_frame.pack(fill="x", padx=5, pady=5)
        
        set_all_btn = ctk.CTkButton(
            set_all_frame,
            text="Set Placement For All",
            command=self._set_all_placements
        )
        set_all_btn.pack(pady=5)
        
        # Create new widgets for each context in the scrollable frame
        for context in contexts:
            frame = ctk.CTkFrame(self.context_scroll)
            frame.pack(fill="x", padx=5, pady=2)
            
            label = ctk.CTkLabel(frame, text=f"Settings for {context}:")
            label.pack(side="left", padx=5)
            
            button_frame = ctk.CTkFrame(frame)
            button_frame.pack(side="right", padx=5)
            
            set_btn = ctk.CTkButton(
                button_frame,
                text="Set Placement",
                command=lambda ctx=context: self._set_context_placement(ctx),
                width=100
            )
            set_btn.pack(side="left", padx=2)
            
            confirm_btn = ctk.CTkButton(
                button_frame,
                text="Confirm",
                command=lambda ctx=context: self._confirm_placement(ctx),
                width=100,
                state="disabled"
            )
            confirm_btn.pack(side="left", padx=2)
            
            # Store both buttons for this context
            self.context_widgets[context] = {
                'frame': frame,
                'set_btn': set_btn,
                'confirm_btn': confirm_btn,
                'confirmed': False
            }
    
    def _set_context_placement(self, context: str):
        """Set placement settings for a context using a sample image"""
        # Check if there's an active session
        if self.placement_handler.has_active_session():
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', "⚠️ Please complete the current placement before starting another!\n")
            self.status_text.insert('end', "="*50 + "\n\n")
            return
            
        # Check for watermark first
        if not os.path.exists(self.watermark_path):
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', "❌ ERROR: Please select a watermark file first\n")
            self.status_text.insert('end', "="*50 + "\n\n")
            return
            
        folder = self.folder_entry.get()
        
        try:
            # Disable all Set Placement buttons during processing
            for widgets in self.context_widgets.values():
                widgets['set_btn'].configure(state="disabled")
            
            # Find a sample image for this context
            sample_image = None
            if self.mode_var.get() == "single":
                for file in os.listdir(folder):
                    if context in file.lower() and file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        sample_image = os.path.join(folder, file)
                        break
            else:
                for root, _, files in os.walk(folder):
                    for file in files:
                        if context in file.lower() and file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            sample_image = os.path.join(root, file)
                            break
                    if sample_image:
                        break
            
            if not sample_image:
                self.status_text.insert('end', "\n" + "="*50 + "\n")
                self.status_text.insert('end', f"❌ ERROR: No sample image found for context: {context}\n")
                self.status_text.insert('end', "="*50 + "\n\n")
                return
            
            # Convert to Windows path format
            sample_image = os.path.normpath(sample_image)
            
            # Reset confirmation state
            self.context_widgets[context]['confirmed'] = False
            confirm_btn = self.context_widgets[context]['confirm_btn']
            
            self.status_text.insert('end', f"\nRestarting placement process for {context}:\n")
            self.status_text.insert('end', "1. Background will be removed automatically\n")
            self.status_text.insert('end', "2. Position and resize the image as desired\n")
            self.status_text.insert('end', "3. If you resized or rotated the image:\n")
            self.status_text.insert('end', "   - Click the checkmark (✓) in Photoshop\n")
            self.status_text.insert('end', "   - Or press Enter\n")
            self.status_text.insert('end', "   - Or click outside the transform box\n")
            self.status_text.insert('end', "4. AFTER committing any changes, click 'Confirm Image Position'\n")
            self.status_text.insert('end', "5. Position the watermark\n")
            self.status_text.insert('end', "6. If you resized the watermark, commit changes as in step 3\n")
            self.status_text.insert('end', "7. AFTER committing any changes, click 'Confirm Watermark Position'\n\n")
            
            try:
                # Open placement session
                self.placement_handler.set_placement_interactively(sample_image, context)
                # Enable confirm button and reset its state
                confirm_btn.configure(
                    state="normal",
                    text="Confirm Image Position",
                    fg_color="#1f538d",  # Default blue color
                    hover_color="#2765b0"  # Slightly lighter blue for hover
                )
                self.status_text.insert('end', f"Background removed. Position the image in Photoshop.\n")
                self.status_text.insert('end', f"⚠️ If you resize/rotate, commit the changes (✓ or Enter) BEFORE clicking 'Confirm Image Position'\n")
            except Exception as e:
                self.status_text.insert('end', "\n" + "="*50 + "\n")
                self.status_text.insert('end', f"❌ ERROR setting placement for {context}: {str(e)}\n")
                self.status_text.insert('end', f"Sample image path: {sample_image}\n")
                self.status_text.insert('end', "Please check if the file exists and is accessible\n")
                self.status_text.insert('end', "="*50 + "\n\n")
        
        except Exception as e:
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', f"❌ ERROR in _set_context_placement: {str(e)}\n")
            self.status_text.insert('end', "="*50 + "\n\n")
        finally:
            # Re-enable all Set Placement buttons
            for widgets in self.context_widgets.values():
                widgets['set_btn'].configure(state="normal")
    
    def _confirm_placement(self, context: str):
        """Confirm placement settings for a context"""
        try:
            self.status_text.insert('end', f"Confirming placement for {context}...\n")
            
            # Disable all buttons during confirmation
            for widgets in self.context_widgets.values():
                widgets['set_btn'].configure(state="disabled")
                if widgets['confirm_btn'].cget('text') != "CONFIRMED":
                    widgets['confirm_btn'].configure(state="disabled")
            
            # Get settings from current session
            settings = self.placement_handler.confirm_placement()
            if settings:
                self.context_settings[context] = settings
                
                # Check if this was the first confirmation (image placement)
                confirm_btn = self.context_widgets[context]['confirm_btn']
                if confirm_btn.cget('text') == "Confirm Image Position":
                    # Update button for watermark confirmation
                    confirm_btn.configure(
                        text="Confirm Watermark Position",
                        fg_color="#b8860b",  # Dark golden color
                        state="normal"
                    )
                    self.status_text.insert('end', f"Image position saved. Now position the watermark.\n")
                    self.status_text.insert('end', f"⚠️ If you resize/rotate the watermark, commit the changes (✓ or Enter) BEFORE clicking 'Confirm Watermark Position'\n")
                else:
                    # This was the watermark confirmation
                    if 'output_path' in settings:
                        self.status_text.insert('end', f"Successfully completed placement settings for {context}\n")
                        self.status_text.insert('end', f"Saved processed image to: {settings['output_path']}\n")
                        
                        confirm_btn.configure(
                            state="normal",  # Keep enabled to show completion
                            text="CONFIRMED",
                            fg_color="#2e8b57",  # Sea green color
                            hover_color="#2e8b57"  # Disable hover effect
                        )
                        self.context_widgets[context]['confirmed'] = True
                        
                        # If this was part of Set All, move to next context
                        if hasattr(self, '_set_all_queue') and self._set_all_queue:
                            self._process_next_in_queue()
                    else:
                        self.status_text.insert('end', "\n" + "="*50 + "\n")
                        self.status_text.insert('end', f"❌ ERROR: Failed to save processed image for {context}\n")
                        self.status_text.insert('end', "Please try setting placement again\n")
                        self.status_text.insert('end', "="*50 + "\n\n")
            else:
                self.status_text.insert('end', "\n" + "="*50 + "\n")
                self.status_text.insert('end', f"❌ ERROR: Failed to confirm placement for {context} - no settings returned\n")
                self.status_text.insert('end', "="*50 + "\n\n")
        except Exception as e:
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', f"❌ ERROR confirming placement for {context}: {str(e)}\n")
            self.status_text.insert('end', "Please try setting placement again\n")
            self.status_text.insert('end', "="*50 + "\n\n")
        finally:
            # Re-enable all Set Placement buttons and valid Confirm buttons
            for widgets in self.context_widgets.values():
                widgets['set_btn'].configure(state="normal")
                if not widgets['confirmed']:  # Don't re-enable confirmed buttons
                    widgets['confirm_btn'].configure(state="normal")
    
    def _set_all_placements(self):
        """Start the process of setting placement for all contexts"""
        # Create queue of unconfirmed contexts
        self._set_all_queue = [
            context for context, widgets in self.context_widgets.items()
            if not widgets['confirmed']
        ]
        
        if not self._set_all_queue:
            self.status_text.insert('end', "All contexts already have placement settings\n")
            return
        
        self.status_text.insert('end', "Starting placement settings for all contexts...\n")
        self._process_next_in_queue()
    
    def _process_next_in_queue(self):
        """Process the next context in the Set All queue"""
        if not self._set_all_queue:
            self.status_text.insert('end', "Finished setting placement for all contexts\n")
            return
            
        next_context = self._set_all_queue.pop(0)
        self._set_context_placement(next_context)
    
    def _run_processing(self):
        """Run the selected processing operations"""
        if not self.processing_options:
            self.status_text.insert('end', "Please select at least one processing option\n")
            return
            
        folder = self.folder_entry.get()
        if not folder:
            self.status_text.insert('end', "Please select a folder first\n")
            return
        
        # Clear status text
        self.status_text.delete('1.0', 'end')
        self.status_text.insert('end', "Starting processing...\n")
        
        # Disable buttons during processing
        self.run_btn.configure(state="disabled")
        self.analyze_btn.configure(state="disabled")
        
        try:
            def update_status(msg: str):
                self.status_text.insert('end', f"{msg}\n")
                self.status_text.see('end')
                self.update()  # Update GUI
            
            # Run processing
            self.image_processor.process_images(
                folder=folder,
                is_mass_mode=self.mode_var.get() == "mass",
                operations=self.processing_options,
                context_settings=self.context_settings,
                status_callback=update_status
            )
            
            self.status_text.insert('end', "Processing complete!\n")
            
        except Exception as e:
            self.status_text.insert('end', f"Error during processing: {str(e)}\n")
            
        finally:
            # Re-enable buttons
            self.run_btn.configure(state="normal")
            self.analyze_btn.configure(state="normal")
    
    def _clear_output(self):
        """Clear the status text output"""
        self.status_text.delete('1.0', 'end')
    
    def _browse_watermark(self):
        """Handle watermark file browsing"""
        file = ctk.filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file:
            self.watermark_path = file
            self.watermark_entry.delete(0, 'end')
            self.watermark_entry.insert(0, file)
            # Update the handler with new watermark path
            self.placement_handler.watermark_path = file

if __name__ == "__main__":
    app = UnifiedRunnerGUI()
    app.mainloop() 