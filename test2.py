
import subprocess
import sys
import PySimpleGUI as sg


layout = [
    [
        sg.Button('search_column'),
        sg.VSeperator(),  # vertical separator
    ]
]

window = sg.Window('test', layout=layout).read()
sg.ToolTip(window, 'test tooltip')
