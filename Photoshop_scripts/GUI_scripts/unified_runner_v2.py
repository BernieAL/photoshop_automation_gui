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
        
        # Template/Background Path
        template_frame = ctk.CTkFrame(config_frame)
        template_frame.pack(fill="x", padx=5, pady=5)
        
        template_label = ctk.CTkLabel(template_frame, text="Background Template: (if any)")
        template_label.pack(side="left", padx=5)
        
        self.template_entry = ctk.CTkEntry(template_frame, width=400)
        self.template_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.template_entry.insert(0, self.template_path)
        
        template_browse = ctk.CTkButton(
            template_frame,
            text="Browse",
            command=self._browse_template,
            width=100
        )
        template_browse.pack(side="right", padx=5)
        
        # Watermark Path and Setup
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
        
        # Watermark Position Mode
        watermark_mode_frame = ctk.CTkFrame(config_frame)
        watermark_mode_frame.pack(fill="x", padx=5, pady=5)
        
        self.watermark_mode_var = ctk.BooleanVar(value=False)  # Changed from True to False
        
        watermark_mode_checkbox = ctk.CTkCheckBox(
            watermark_mode_frame,
            text="Use default watermark position for all images",
            variable=self.watermark_mode_var,
            command=self._on_watermark_mode_change
        )
        watermark_mode_checkbox.pack(pady=2)
        
        # Watermark Position Setup Button (for default mode)
        self.watermark_setup_frame = ctk.CTkFrame(config_frame)
        self.watermark_setup_frame.pack(fill="x", padx=5, pady=5)
        
        self.watermark_position_btn = ctk.CTkButton(
            self.watermark_setup_frame,
            text="Set Default Watermark Position",
            command=self._setup_watermark_position,
            width=200
        )
        self.watermark_position_btn.pack(pady=5)
        
        # Label to show watermark position status
        self.watermark_status_label = ctk.CTkLabel(
            self.watermark_setup_frame,
            text="❌ Watermark position not set",
            text_color="red"
        )
        self.watermark_status_label.pack(pady=2)
        
        # Store watermark settings
        self.watermark_settings = None
    
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
                "2. Position and resize the image as desired\n"
                "3. If you resize/rotate the image:\n"
                "   - Click the checkmark (✓) in Photoshop\n"
                "   - Or press Enter\n"
                "   - Or click outside the transform box\n"
                "4. Click 'Confirm' to save the placement\n"
                "\nButton Color Guide:\n"
                "• Blue - Ready for placement\n"
                "• Green - Placement confirmed\n"
                "\nIMPORTANT: After setting all placements,\n"
                "click 'Run Processing' to create the output files.\n"
                "Previous output files will be overwritten."
            ),
            justify="left"
        )
        instructions_label.pack(pady=5, padx=5)
        
        # Add action buttons frame
        action_frame = ctk.CTkFrame(self.context_frame)
        action_frame.pack(fill="x", padx=5, pady=5)
        
        # Add Set All button
        set_all_btn = ctk.CTkButton(
            action_frame,
            text="Set Placement For All",
            command=self._set_all_placements,
            width=200
        )
        set_all_btn.pack(side="left", padx=5, pady=5)
        
        # Add Reset All button
        reset_all_btn = ctk.CTkButton(
            action_frame,
            text="Reset All Placements",
            command=self._reset_all_placements,
            width=200,
            fg_color="#8B0000",  # Dark red
            hover_color="#A52A2A"  # Brown
        )
        reset_all_btn.pack(side="right", padx=5, pady=5)
        
        # Create new widgets for each context in the scrollable frame
        for context in contexts:
            frame = ctk.CTkFrame(self.context_scroll)
            frame.pack(fill="x", padx=5, pady=2)
            
            label = ctk.CTkLabel(frame, text=f"Settings for {context}:")
            label.pack(side="left", padx=5)
            
            button_frame = ctk.CTkFrame(frame)
            button_frame.pack(side="right", padx=5)
            
            # Add Reset button
            reset_btn = ctk.CTkButton(
                button_frame,
                text="Reset",
                command=lambda ctx=context: self._reset_context_placement(ctx),
                width=70,
                fg_color="#8B0000",  # Dark red
                hover_color="#A52A2A"  # Brown
            )
            reset_btn.pack(side="left", padx=2)
            
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
            
            # Add Copy Settings To All button (initially hidden)
            copy_btn = ctk.CTkButton(
                button_frame,
                text="Copy Settings To All",
                command=lambda ctx=context: self._copy_settings_to_all(ctx),
                width=150,
                fg_color="#4B0082",  # Indigo
                hover_color="#663399"  # Rebecca Purple
            )
            # Will be packed when context is confirmed
            
            # Store buttons for this context
            self.context_widgets[context] = {
                'frame': frame,
                'reset_btn': reset_btn,
                'set_btn': set_btn,
                'confirm_btn': confirm_btn,
                'copy_btn': copy_btn,
                'confirmed': False
            }
            
    def _reset_context_placement(self, context: str):
        """Reset placement settings for a specific context"""
        try:
            # Remove context from settings
            if context in self.context_settings:
                del self.context_settings[context]
            
            # Reset button states
            widgets = self.context_widgets[context]
            widgets['confirmed'] = False
            widgets['confirm_btn'].configure(
                state="disabled",
                text="Confirm",
                fg_color="#1f538d",  # Default blue
                hover_color="#2765b0"
            )
            # Hide Copy Settings To All button
            widgets['copy_btn'].pack_forget()
            
            self.status_text.insert('end', f"Reset placement settings for {context}\n")
            
        except Exception as e:
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', f"❌ ERROR resetting {context}: {str(e)}\n")
            self.status_text.insert('end', "="*50 + "\n\n")
            
    def _reset_all_placements(self):
        """Reset all placement settings"""
        try:
            # Clear all settings
            self.context_settings.clear()
            
            # Reset all button states
            for context, widgets in self.context_widgets.items():
                widgets['confirmed'] = False
                widgets['confirm_btn'].configure(
                    state="disabled",
                    text="Confirm",
                    fg_color="#1f538d",  # Default blue
                    hover_color="#2765b0"
                )
                # Hide Copy Settings To All button
                widgets['copy_btn'].pack_forget()
            
            self.status_text.insert('end', "Reset all placement settings\n")
            
        except Exception as e:
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', f"❌ ERROR resetting all placements: {str(e)}\n")
            self.status_text.insert('end', "="*50 + "\n\n")
    
    def _set_context_placement(self, context: str):
        """Set placement settings for a context using a sample image"""
        # Check if there's an active session
        if self.placement_handler.has_active_session():
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', "⚠️ Please complete the current placement before starting another!\n")
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
            
            self.status_text.insert('end', f"\nSetting up placement for {context}:\n")
            self.status_text.insert('end', "1. Background will be removed automatically\n")
            self.status_text.insert('end', "2. Position and resize the image as desired\n")
            self.status_text.insert('end', "3. If you resize/rotate the image:\n")
            self.status_text.insert('end', "   - Click the checkmark (✓) in Photoshop\n")
            self.status_text.insert('end', "   - Or press Enter\n")
            self.status_text.insert('end', "   - Or click outside the transform box\n")
            self.status_text.insert('end', "4. Click 'Confirm' to save the placement\n\n")
            
            try:
                # Open placement session
                self.placement_handler.set_placement_interactively(sample_image, context)
                # Enable confirm button and reset its state
                confirm_btn.configure(
                    state="normal",
                    text="Confirm",
                    fg_color="#1f538d",  # Default blue color
                    hover_color="#2765b0"  # Slightly lighter blue for hover
                )
                self.status_text.insert('end', f"Background removed. Position the image in Photoshop.\n")
                self.status_text.insert('end', f"⚠️ If you resize/rotate, commit the changes (✓ or Enter) BEFORE clicking 'Confirm'\n")
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
            
            # Check if we have an active session
            if not self.placement_handler.has_active_session():
                self.status_text.insert('end', "\n" + "="*50 + "\n")
                self.status_text.insert('end', "❌ ERROR: No active placement session\n")
                self.status_text.insert('end', "Please click 'Set Placement' to start a new session\n")
                self.status_text.insert('end', "="*50 + "\n\n")
                return
            
            # Get settings from current session
            settings = self.placement_handler.confirm_placement()
            if settings:
                # Store settings
                if 'watermark' in settings:
                    # This was the final confirmation with watermark settings
                    self.context_settings[context] = settings
                    
                    if 'output_path' in settings:
                        self.status_text.insert('end', f"Successfully completed placement and watermark settings for {context}\n")
                        self.status_text.insert('end', "⚠️ Remember to click 'Run Processing' to create the output files\n")
                        
                        confirm_btn = self.context_widgets[context]['confirm_btn']
                        confirm_btn.configure(
                            state="normal",  # Keep enabled to show completion
                            text="CONFIRMED",
                            fg_color="#2e8b57",  # Sea green color
                            hover_color="#2e8b57"  # Disable hover effect
                        )
                        self.context_widgets[context]['confirmed'] = True
                        
                        # Show Copy Settings To All button
                        self.context_widgets[context]['copy_btn'].pack(side="left", padx=2)
                        
                        # If this was part of Set All, move to next context
                        if hasattr(self, '_set_all_queue') and self._set_all_queue:
                            self._process_next_in_queue()
                    else:
                        self.status_text.insert('end', "\n" + "="*50 + "\n")
                        self.status_text.insert('end', f"❌ ERROR: Failed to save settings for {context}\n")
                        self.status_text.insert('end', "Please try setting placement again\n")
                        self.status_text.insert('end', "="*50 + "\n\n")
                else:
                    # This was the first confirmation, now waiting for watermark
                    if not self.watermark_mode_var.get():  # Individual watermark mode
                        self.context_settings[context] = settings  # Store initial settings
                        confirm_btn = self.context_widgets[context]['confirm_btn']
                        confirm_btn.configure(
                            text="Confirm Watermark",
                            fg_color="#b8860b",  # Dark golden color
                            state="normal"
                        )
                        self.status_text.insert('end', f"Image position saved. Now position the watermark.\n")
                        self.status_text.insert('end', "Watermark Adjustment Options:\n")
                        self.status_text.insert('end', "- Resize the watermark by dragging the corners\n")
                        self.status_text.insert('end', "- Move to desired position\n")
                        self.status_text.insert('end', "- Adjust opacity in the Layers panel\n\n")
                        self.status_text.insert('end', f"⚠️ After making adjustments, commit the changes (✓ or Enter) BEFORE clicking 'Confirm Watermark'\n")
                        
                        # Start watermark placement session
                        self.placement_handler.start_watermark_placement()
                    else:
                        # In default watermark mode, complete immediately
                        self.context_settings[context] = settings
                        if 'output_path' in settings:
                            self.status_text.insert('end', f"Successfully completed placement settings for {context}\n")
                            
                            confirm_btn = self.context_widgets[context]['confirm_btn']
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
            
        # Check watermark requirements
        needs_watermark = ("Add Watermark ONLY" in self.processing_options or 
                         "Custom Placement + Background Removal + Watermark" in self.processing_options)
        
        if needs_watermark:
            if self.watermark_mode_var.get():  # Using default watermark position
                if not self.watermark_settings:
                    self.status_text.insert('end', "\n" + "="*50 + "\n")
                    self.status_text.insert('end', "❌ ERROR: Please set the default watermark position first\n")
                    self.status_text.insert('end', "="*50 + "\n\n")
                    return
            else:  # Using individual watermark positions
                # Get watermark settings from the first context that has them
                for context_settings in self.context_settings.values():
                    if 'watermark' in context_settings:
                        self.watermark_settings = context_settings['watermark']
                        break
                if not self.watermark_settings:
                    self.status_text.insert('end', "\n" + "="*50 + "\n")
                    self.status_text.insert('end', "❌ ERROR: No watermark settings found in any context\n")
                    self.status_text.insert('end', "="*50 + "\n\n")
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
            
            # Pass watermark settings to image processor
            if self.watermark_settings:
                self.image_processor.set_watermark_settings(self.watermark_settings)
            
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

    def _browse_template(self):
        """Handle template/background file browsing"""
        file = ctk.filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.psd"),
                ("All files", "*.*")
            ]
        )
        if file:
            self.template_path = file
            self.template_entry.delete(0, 'end')
            self.template_entry.insert(0, file)
            # Update handlers with new template path
            self.placement_handler.template_path = file
            self.image_processor.template_path = file

    def _setup_watermark_position(self):
        """Set up the default watermark position that will be used for all images"""
        if not os.path.exists(self.watermark_path):
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', "❌ ERROR: Please select a watermark file first\n")
            self.status_text.insert('end', "="*50 + "\n\n")
            return
            
        try:
            self.status_text.insert('end', "\nSetting up default watermark position...\n")
            
            # Use the new capture_watermark_settings method
            if self.image_processor.capture_watermark_settings(
                status_callback=lambda msg: self.status_text.insert('end', msg + "\n")
            ):
                # Update status
                self.watermark_status_label.configure(
                    text="✅ Watermark position set",
                    text_color="green"
                )
                self.watermark_settings = self.image_processor.watermark_settings
            else:
                self.status_text.insert('end', "\n" + "="*50 + "\n")
                self.status_text.insert('end', "❌ Failed to capture watermark settings\n")
                self.status_text.insert('end', "="*50 + "\n\n")
                
        except Exception as e:
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', f"❌ ERROR setting up watermark: {str(e)}\n")
            self.status_text.insert('end', "="*50 + "\n\n")

    def _on_watermark_mode_change(self):
        """Handle watermark mode change"""
        if self.watermark_mode_var.get():
            # Show default watermark setup
            self.watermark_setup_frame.pack(fill="x", padx=5, pady=5)
        else:
            # Hide default watermark setup
            self.watermark_setup_frame.pack_forget()
            # Clear default watermark settings
            self.watermark_settings = None
            self.watermark_status_label.configure(
                text="❌ Individual watermark positioning enabled",
                text_color="orange"
            )
            
    def _copy_settings_to_all(self, source_context: str):
        """Copy placement settings from one context to all others"""
        try:
            if source_context not in self.context_settings:
                self.status_text.insert('end', "\n" + "="*50 + "\n")
                self.status_text.insert('end', f"❌ ERROR: No settings found for {source_context}\n")
                self.status_text.insert('end', "="*50 + "\n\n")
                return
                
            source_settings = self.context_settings[source_context]
            
            # Apply to all unconfirmed contexts
            for context, widgets in self.context_widgets.items():
                if context != source_context and not widgets['confirmed']:
                    # Copy settings but preserve context-specific info
                    self.context_settings[context] = source_settings.copy()
                    
                    # Update button states
                    widgets['confirmed'] = True
                    widgets['confirm_btn'].configure(
                        state="normal",
                        text="CONFIRMED",
                        fg_color="#2e8b57",  # Sea green color
                        hover_color="#2e8b57"  # Disable hover effect
                    )
            
            self.status_text.insert('end', f"Successfully copied settings from {source_context} to all other contexts\n")
            self.status_text.insert('end', "⚠️ Remember to click 'Run Processing' to create the output files\n")
            
        except Exception as e:
            self.status_text.insert('end', "\n" + "="*50 + "\n")
            self.status_text.insert('end', f"❌ ERROR copying settings: {str(e)}\n")
            self.status_text.insert('end', "="*50 + "\n\n")

if __name__ == "__main__":
    app = UnifiedRunnerGUI()
    app.mainloop() 