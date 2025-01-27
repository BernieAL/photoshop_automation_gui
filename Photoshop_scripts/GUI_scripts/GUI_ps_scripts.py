import tkinter as tk
import tkinter.ttk as ttk
import os
import subprocess

class GUI:
    def __init__(self):
        # ... existing init code ...

        # Add calibration button
        self.calibrate_button = ttk.Button(
            self.main_frame,
            text="Calibrate Watermark",
            command=self.run_calibration
        )
        self.calibrate_button.pack(pady=5)

    def run_calibration(self):
        """Runs the watermark calibration script"""
        calibration_script = os.path.join(
            self.scripts_dir_path, 
            'watermark_calibration.py'
        )
        if os.path.isfile(calibration_script):
            try:
                subprocess.run(["python", calibration_script])
            except FileNotFoundError:
                print("Calibration script not found.") 