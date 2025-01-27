"""
GUI for Photoshop script selection and folder processing
"""
import customtkinter as ctk
import os.path
import subprocess

class PhotoshopAutomationGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Photoshop Automation")
        self.geometry("800x600")

        # Get scripts
        self.scripts_dir_path = os.path.join(os.getcwd(), 'Photoshop_scripts/ps_scripts')
        self.scripts = os.listdir(self.scripts_dir_path)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Folder selection
        self.folder_frame = ctk.CTkFrame(self.main_frame)
        self.folder_frame.pack(fill="x", padx=10, pady=5)

        self.folder_label = ctk.CTkLabel(
            self.folder_frame, 
            text="Source Folder - Paste Path or Browse"
        )
        self.folder_label.pack(side="left", padx=5)

        self.folder_entry = ctk.CTkEntry(
            self.folder_frame, 
            width=300
        )
        self.folder_entry.pack(side="left", padx=5)

        self.browse_button = ctk.CTkButton(
            self.folder_frame, 
            text="Browse",
            command=self.browse_folder
        )
        self.browse_button.pack(side="left", padx=5)

        # Script selection
        self.script_frame = ctk.CTkFrame(self.main_frame)
        self.script_frame.pack(fill="x", padx=10, pady=5)

        self.script_label = ctk.CTkLabel(
            self.script_frame, 
            text="Select Script to Run"
        )
        self.script_label.pack(side="left", padx=5)

        self.script_combo = ctk.CTkComboBox(
            self.script_frame,
            values=self.scripts,
            width=300
        )
        self.script_combo.pack(side="left", padx=5)

        # File list
        self.file_list = ctk.CTkTextbox(
            self.main_frame,
            width=400,
            height=300
        )
        self.file_list.pack(pady=10)

        # Submit button
        self.submit_button = ctk.CTkButton(
            self.main_frame,
            text="Run Script",
            command=self.run_script
        )
        self.submit_button.pack(pady=10)

    def browse_folder(self):
        folder = ctk.filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, 'end')
            self.folder_entry.insert(0, folder)
            self.update_file_list(folder)

    def update_file_list(self, folder):
        try:
            file_list = os.listdir(folder)
            self.file_list.delete('1.0', 'end')
            self.file_list.insert('1.0', '\n'.join(file_list))
        except:
            self.file_list.delete('1.0', 'end')
            self.file_list.insert('1.0', "Error reading folder")

    def run_script(self):
        selected_script = self.script_combo.get()
        selected_folder = self.folder_entry.get()

        if selected_script and selected_folder:
            selected_script_path = os.path.join(self.scripts_dir_path, selected_script)
            if os.path.isfile(selected_script_path):
                try:
                    # Use the virtual environment's Python interpreter
                    python_path = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')
                    if not os.path.exists(python_path):
                        # Fallback to system Python if venv not found
                        python_path = 'python'
                    subprocess.run([python_path, selected_script_path, selected_folder])
                except FileNotFoundError:
                    print(f"Script '{selected_script}' not found.")

if __name__ == "__main__":
    app = PhotoshopAutomationGUI()
    app.mainloop()


"""
resources

https://realpython.com/pysimplegui-python/#getting-started-with-pysimplegui
https://www.tutorialspoint.com/pysimplegui/pysimplegui_combo_element.htm
https://stackoverflow.com/questions/57200315/connect-process-a-script-to-pysimplegui-button
https://www.pysimplegui.org/en/latest/cookbook/


"""