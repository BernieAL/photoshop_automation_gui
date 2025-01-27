#UNFINISHED!!!!!!!!!!!! DOES NOT WORK



import PySimpleGUI as sg
import os.path
import subprocess

# REF https://stackoverflow.com/questions/59500558/how-to-display-different-layouts-based-on-button-clicks-in-pysimple-gui-persis



"""
prompt user for store token(later)
prompt user for BP ID
pull details for BP ID
pull print providers
select print providers
pull variants
select variant
pull placeholders
ask what placeholders to use
ask what image to use
create
"""

scripts_dir_path = os.path.join(os.getcwd(),'printify_scripts/scripts')
scripts_list = os.listdir(scripts_dir_path)
# print(scripts)

"""
This is a dropdown for user to select script to run
Depending on which script is selected, we hide certain columns and show others
"""
script_selection_col =  [
    [
        sg.Text("Select Script to Run"),
        sg.Combo(scripts_list,font=('Arial Bold', 14), expand_x=True,enable_events=True,readonly=True,key='-SCRIPT-'),
    ],
    [
        sg.Button("Submit")
    ]
]

product_builder_col = [ 
    [
        sg.Text("Enter The Following Information To Create Product"),
        sg.In(size=(40,1),enable_events=True,key='-PRODUCT_BUILDER-'),
    ],
    [
        sg.Button("Submit")
    ]
]

# layout3 = [

# ]

main_layout = [
    [
        # sg.Column(src_folder_selection_col),
        # sg.VSeparator(),
        sg.Column(script_selection_col),
        sg.Column(product_builder_col,visible=False)
    ]
]



window = sg.Window("File Path Input",main_layout)





layout = 1 #the currently visible layout
while True:
    event,values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    
    #if event key is -FOLDER-, 
    if event == "-FOLDER-":
        
        #get the selected folder from component values
        folder=values["-FOLDER-"]
        try:
            #list all files in selected folder
            file_list = os.listdir(folder)
        except:
            file_list = []
        
        #update -FILE LIST- component with list of files
        window['-FILE LIST-'].update(file_list)

    #if event key is -SUBMIT-
    if event == "Submit":
        
        #get the selected  script value from component values
        selected_script = values["-SCRIPT-"]
        print(selected_script)

        if selected_script == 'product_creation.py':
            window['-SCRIPT-'].update(visible=False)
            window['-PRODUCT_BUILDER-'].update(visible=True)
    


window.close()