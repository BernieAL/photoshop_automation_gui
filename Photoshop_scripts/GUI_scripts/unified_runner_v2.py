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
    REMOVE_BG = "Remove Background"
    ADD_WATERMARK = "Add Watermark"
    CUSTOM_PLACEMENT = "Custom Placement & Background"
    
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
        
        # State variables
        self.selected_folders = []
        self.processing_options = set()
        self.context_settings = {}  # Stores placement settings for each context
        
        # Initialize handlers
        self.template_path = "C:/Users/balma/Documents/ecommerce/lady cosmica/background listing templates/base-template.png"  # TODO: Make configurable
        self.watermark_path = "C:/Users/balma/Documents/ecommerce/lady cosmica/graphics-watermarks-backgrounds/Lady-Cosmica-Watermark.png"  # TODO: Make configurable
        self.placement_handler = ContextPlacementHandler(self.template_path)
        self.image_processor = ImageProcessor(self.template_path, self.watermark_path)
        
        self._create_gui()
    
    def _create_gui(self):
        """Create the main GUI elements"""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
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
            text="Context Settings",
            font=("Arial", 14, "bold")
        )
        self.context_label.pack(pady=5)
        
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
        self.status_text = ctk.CTkTextbox(
            self.main_frame,
            height=200,
            width=600
        )
        self.status_text.pack(fill="x", padx=10, pady=10)
    
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
        
        # Create new widgets for each context
        for context in contexts:
            frame = ctk.CTkFrame(self.context_frame)
            frame.pack(fill="x", padx=5, pady=5)
            
            label = ctk.CTkLabel(frame, text=f"Settings for {context}:")
            label.pack(side="left", padx=5)
            
            set_btn = ctk.CTkButton(
                frame,
                text="Set Placement",
                command=lambda ctx=context: self._set_context_placement(ctx)
            )
            set_btn.pack(side="left", padx=5)
            
            self.context_widgets[context] = frame
    
    def _set_context_placement(self, context: str):
        """Open Photoshop to set placement for a context"""
        folder = self.folder_entry.get()
        if not folder:
            self.status_text.insert('end', "Please select a folder first\n")
            return
            
        # Find first image with this context
        sample_image = None
        if self.mode_var.get() == "single":
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    if self._extract_context(file) == context:
                        sample_image = os.path.join(folder, file)
                        break
        else:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        if self._extract_context(file) == context:
                            sample_image = os.path.join(root, file)
                            break
                if sample_image:
                    break
        
        if not sample_image:
            self.status_text.insert('end', f"No sample image found for context: {context}\n")
            return
            
        self.status_text.insert('end', f"Setting placement for {context} using {sample_image}...\n")
        
        try:
            # Get placement settings interactively
            settings = self.placement_handler.set_placement_interactive(context, sample_image)
            self.context_settings[context] = settings
            
            self.status_text.insert('end', f"Successfully saved placement settings for {context}\n")
            
        except Exception as e:
            self.status_text.insert('end', f"Error setting placement for {context}: {str(e)}\n")
    
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

if __name__ == "__main__":
    app = UnifiedRunnerGUI()
    app.mainloop() 