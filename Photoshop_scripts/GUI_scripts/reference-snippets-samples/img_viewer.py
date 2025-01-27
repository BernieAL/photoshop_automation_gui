#img_viewer.py

# https://realpython.com/pysimplegui-python/#getting-started-with-pysimplegui


import PySimpleGUI as sg
import os.path

#first - window layout in 2 cols

file_list_column = [
    [
        sg.Text("Image Folder"),
        sg.In(size=(25,1),enable_events=True,key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[],enable_events=True,size=(40,20),key="-FILE LIST-"
        )
    ],
]

image_viewer_column=[
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40,1),key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
]

layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Image Viewer",layout)

while True:
    event,values = window.read()
    if event == "EXIT" or event == sg.WIN_CLOSED:
        break
    
    # folder name was filled in, make a list of files in the folder
    #check for event with key -FOLDER-
    if event == "-FOLDER-":
        folder=values["-FOLDER-"]
        try:
            #GET LIST OF FILES IN FOLDER
            file_list = os.listdir(folder)
        except:
            # set to empty list
            file_list = []


        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder,f))
            and f.lower().endswith((".png",".gif"))
        ]
        window["-FILE LIST-"].update(fnames)
    
    # file was chosen from the listbox
    elif event =="-FILE LIST-": 
        try:
            filename = os.path.join(
                values["-FOLDER-"],values["-FILE LIST-"][0]
            )
            window['-TOUT-'].update(filename)
            window['-IMAGE-'].update(filename=filename)
        except:
            pass


window.close()


"""
Nested elements in a col are placed IN col as rows

LEFT COL - This is File list col
    
     [
        sg.Text("Image Folder"),
        sg.In(size=(25,1),enable_events=True,key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[],enable_events=True,size=(40,20),key="-FILE LIST-"
        )
    ],

    Key parameter
        used to identify a specific element in GUI

        for In(),input text control, we give identity of "-FOLDER-"
        we -FOLDER- to access content of element
        And events are enabled for this element -> enable_events=True

    ListBox() element displays a list of paths to images you can choose from to display
    when first loading the ListBox() element, we want to to be empty, so we pass it an empty list
    for ListBox() we turn on events, set its size and give it unique ID

RIGHT COL - This is image_view col
    creates 3 elements
    first element tells user they should choose image to display
    second element display name of selected file
    third displays the image
    
Vertical Seperator
    VSeperator() is an alias for VerticalSeparator()


Defining Layout
    specifying layout contains code that controls how the elements are laid out on screen
    we create 2 columns seperated by VS
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),

Event loop has the logic of the program
extract events and values from the window.
the event will be the key string of whichever element the user interacts with 
values var contains python dict that maps the element key to a value
    Ex. if user picks a folder -> then "-FOLDER-" will map to the folder path
    
values var contains python dic that maps the element key to a value



"""