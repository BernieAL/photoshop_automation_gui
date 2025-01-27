import PySimpleGUI as sg


#create layout
layout = [
    [sg.Text("hello from PySimpleGUI")],
    [sg.Button("OK")]
]

#create window
window = sg.Window("Demo",layout)

#Create event loop
while True:
    event,values = window.read()
    #end program if user closes window or 
    #presses ok button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()


"""
PySimpleGUI has 4 ports
    Tkinter
    PyQT
    wxPython
    Remi

Install
    $ python -m pip install pysimplegui


Creating Basic UI elements 
    widget is generic term to describe elements that make up the user interface
    in pSGUI widgets are elements


Basic Building Block is a Window()
    To create basic window

    import PySimpleGUI as sg

    sg.Window(title="Hello World", layout=[[]], margins=(100, 50)).read()

    window() takes alot of diff args
    for this ex, we gave the window() a title and a layout, and set the margins -which is how big it will
    be in pixels

    read() returns events triggered in the Window(), as a string and a values dictionary
    
    normally you have other elements besides a window in the app
    ex text and a button

PySimpleGUI uses neseted python lists to lay out its elements
you create the layout and pass it to the window

last block of code is the event loop 
a GUI needs to run inside a loop and wait for user to do something
ex- user might need to press a button UI or typ esomething into keyboard
when this happens, the events are processed in event loop

create inifinite while loop sht areads events from the window object
if user presses OK or EXIT, you want the program to end
    to accomplish this, break out of the loop and close() the window

"""