# Import modules
from genericpath import exists
import textwrap
from tkinter.tix import BALLOON, Balloon
import webbrowser
import os
import os.path
import PySimpleGUI as sg
import gi
gi.require_version('Gtk', '2.0')
from gi.repository import Gtk

# Initialize configs
apps = []

for app in sorted(os.listdir('/home/pi/pi-apps/apps')):
    if app != 'template':
        apps.append(app)

font = Gtk.Settings.get_default().get_property("gtk-font-name")
default_font_name = font.split(',')[0].replace(' ', '')
default_font_size = font[-2:]
default_font = default_font_name + ' ' + default_font_size


app_categories = [
    'All Apps',
    'Imported',
    'Tools',
    'Games',
    'Internet',
    'Editors',
    'Multimedia',
    'Browsers',
    'Appearance',
]

# Create app list and tree data
app_list = []
i = 0
treedata = sg.TreeData()
for category in sorted(app_categories):
    app_list.append(category)
    if category != 'Browsers':
        icon = '/home/pi/pi-apps/icons/categories/' + category + '.png'
    else:
        icon = '/home/pi/pi-apps/icons/categories/Browsers.png'
    treedata.insert('', i, ' ' + str(category), [], icon=icon)
    i += 1
current_category = 'Category List'

def back_to_category_list():
    global app_list
    global current_category
    global treedata
    app_list = []
    i = 0
    treedata = sg.TreeData()
    for category in sorted(app_categories):
        app_list.append(category)
        if category != 'Browsers':
            icon = '/home/pi/pi-apps/icons/categories/' + category + '.png'
        else:
            icon = '/home/pi/pi-apps/icons/categories/Browsers.png'
        treedata.insert('', i, ' ' + str(category), [], icon=icon)
        i += 1
        
    window['-APP LIST-'].update(treedata)
    window['-MENU BACK-'].update(visible=False)
    window['-TOOLTIP-'].update('')
    window['-SEARCH-'].update('')

    current_category = 'Category List'

def show_category(category):
        global app_list
        global current_category
        if category == 'All Apps':
            category_apps = os.popen('/home/pi/pi-apps/api list_apps cpu_installable').read().split('\n')          
            i = 0
            treedata = sg.TreeData()
            app_list = []
            i = 0
            for app in category_apps:
                if app != 'template':
                    app_list.append(app)
                    icon = '/home/pi/pi-apps/apps/' + app + '/icon-24.png'
                    treedata.insert('', i, ' ' + str(app), [], icon=icon)
                    
                    i += 1
            window['-APP LIST-'].update(treedata)
            window['-MENU BACK-'].update(visible=True)

        else:
                category_apps = os.popen('cat /home/pi/pi-apps/etc/categories /home/pi/pi-apps/data/category-overrides | grep ' + category + ' | sed "s/|.*//g"').read().split('\n')               
                i = 0
                treedata = sg.TreeData()
                app_list = []
                for app in category_apps:
                    if app != 'template':
                        app_list.append(app)
                        icon = '/home/pi/pi-apps/apps/' + app + '/icon-24.png'
                        treedata.insert('', i, ' ' + str(app), [], icon=icon)
                        
                        i += 1
                window['-APP LIST-'].update(treedata)
                window['-MENU BACK-'].update(visible=True)

        window['-TOOLTIP-'].update(first_line)
        current_category = category

def load_app_info(app):
    global current_app
    status_text = os.popen('cat "/home/pi/pi-apps/data/status/' + app + '" 2>/dev/null').read().rstrip('\n')
    if status_text == '':
        status_text = 'uninstalled'
    website_text = os.popen('cat "/home/pi/pi-apps/apps/' +
                            app + '/website" 2>/dev/null').read().rstrip('\n')

    description_text = os.popen('cat "/home/pi/pi-apps/apps/' +
                                app + '/description"').read()

    window["-APP NAME-"].update(app,
                                font=default_font_name + ' ' + str(20) + ' bold')
    window["-APP ICON-"].update(
        filename='/home/pi/pi-apps/apps/' + app + '/icon-64.png')
    window["-STATUS-"].update("Status:   " + status_text)
    if website_text != '':
        window["-WEBSITE_1-"].update("Website:")
        window["-WEBSITE_2-"].update(website_text)
    else:
        window["-WEBSITE_1-"].update("")
        window["-WEBSITE_2-"].update('')

    window["-GITHUB BUTTON-"].update(visible=False)
    window["-WEBSITE BUTTON-"].update(visible=False)
    window["-DESCRIPTION-"].update(description_text)
    window["-SCRIPTS-"].update(visible=True)
    window["-CREDITS-"].update(visible=True)


    if status_text == 'uninstalled':
        window["-INSTALL BUTTON-"].update(visible=True, image_filename='/home/pi/pi-apps/icons/install.png')
    elif status_text == 'installed':
        window["-INSTALL BUTTON-"].update(visible=True, image_filename='/home/pi/pi-apps/icons/uninstall.png')
    current_app = app

# Create search column layout
search_column = [
    [
        sg.Image(filename='/home/pi/pi-apps/icons/proglogo.png', size=(400, 120))
    ],
    [
        sg.Text('\n')
    ],
    [
        sg.Text("Search apps: ", font=default_font),
        sg.In(size=(25, 1), enable_events=True,
              key="-SEARCH-", font=default_font),
    ],
    [
        sg.Text('')
    ],
    [
        sg.Column([[sg.Text('', key='-TOOLTIP-', size=(65, 6))]], pad=(0, 0), element_justification='center')
    ],
    [
        sg.Tree(treedata, headings='', num_rows=12,
        select_mode='browse', enable_events=True, key='-APP LIST-', font=default_font, col0_width=40, row_height=30, auto_size_columns=False),
    ],
    [
        sg.Button(key='-MENU BACK-', image_filename='/home/pi/pi-apps/icons/back.png', button_text=' ', visible=False)
    ],
]

# Create app info column layout
app_info_column = [
    [sg.Image(key='-APP ICON-', filename='/home/pi/pi-apps/icons/proglogo.png'),
     sg.Text("", key="-APP NAME-", font=default_font_name + " 14"), sg.Button(key="-GITHUB BUTTON-",
               image_filename='/home/pi/pi-apps/icons/github.png', button_text="             "),  sg.Button(key="-WEBSITE BUTTON-",
               image_filename='/home/pi/pi-apps/icons/website.png', button_text="             ")],
    [sg.Text("""The most popular app store for Raspberry Pi computers.""", key="-STATUS-", font=default_font)],
    [sg.Text(key="-WEBSITE_1-", font=default_font), sg.Text(key="-WEBSITE_2-",
                                                            click_submits=True, text_color='blue', font=default_font + ' underline')],
    [sg.Text(key="-USERS-", font=default_font)],

    [sg.Multiline("""Let's be honest: Linux is harder to master than Windows. 
Sometimes it's not user-friendly, and following an outdated tutorial may break your Raspberry Pi's operating system.
There is no centralized software repository, except for the apt repositories which lack many desktop applications.
Surely there is a better way! There is.
Introducing Pi-Apps, a well-maintained collection of app installation-scripts that you can run with one click.

Pi-Apps now serves over 1,000,000 people and hosts nearly 200 apps.""", key="-DESCRIPTION-", size=(75, 20), font=default_font)],

    [sg.Column([[sg.Button(key="-INSTALL BUTTON-",
               image_filename='/home/pi/pi-apps/icons/install.png', button_text="  ",  expand_x=True, visible=False)]], pad=(0, 0), element_justification='center'), sg.Column([[sg.Button(key="-CREDITS-",
               button_text="Credits", font=default_font, tooltip='See who made the app and who put it on Pi-Apps', visible=False)]], pad=(0, 0), element_justification='center'), sg.Column([[sg.Button(key="-SCRIPTS-",
               tooltip="Script", button_text='   ', image_filename='/home/pi/pi-apps/icons/shellscript.png', font=default_font, visible=False,)]], element_justification='center')],
]

# Combine app_info_column and search_column into main layout
layout = [
    [
        sg.Column(search_column),
        sg.VSeperator(),  # vertical separator
        sg.Column(app_info_column),
    ]
]

# Create window
window = sg.Window("Pi-Apps", layout,
                   icon='/home/pi/pi-apps/icons/logo.png', finalize=True, size=(1250, 800))

# Bindings
window['-APP LIST-'].Widget.configure(show='tree')  
window.Element('-DESCRIPTION-').bind("<FocusIn>", '+FOCUS_IN+')
window.Element('-DESCRIPTION-').bind("<FocusOut>", '+FOCUS_OUT+')
window['-WEBSITE_2-'].bind('<Enter>', '+MOUSE OVER+')
window['-WEBSITE_2-'].bind('<Leave>', '+MOUSE AWAY+')
window['-APP LIST-'].bind('<Motion>', '+MOTION+')            
window['-APP LIST-'].bind('<Leave>', '+MOUSE AWAY+')            
window['-APP LIST-'].bind('<MouseWheel>', '+MOTION+')        
window['-APP LIST-'].bind('<KeyRelease>', '+MOTION+')
window.bind('<Control-r>', '-REFRESH-')
window.bind('<Control-i>', '-INSTALL-')
window.bind('<Control-u>', '-UNINSTALL-')
window.bind('<Control-s>', '-SCRIPTS-')
window.bind('<Control-c>', '-CREDITS-')
old_menu_index = (None, None)

current_app = ''

# Run the Event Loop
while True:
    event, values = window.read()
    app = ''
    search_query = ''
    search_result = ''
    i = None
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-SEARCH-":
        search_query = values["-SEARCH-"]
        search_result = []
        try:
            if search_query != '':
                output = os.popen('/home/pi/pi-apps/api list_apps cpu_installable | /home/pi/pi-apps/api list_intersect "$(/home/pi/pi-apps/api list_apps visible)" | grep -i "' + \
                    search_query + '" | sort').read()
                temp_file = os.popen('mktemp').read().strip('\n')
                f = open(temp_file, 'w')
                f.write(output)
                f.close()
                f = open(temp_file, 'r')

                for line in sorted(f.readlines()):
                    if line != '\n':
                        search_result.append(line.strip("'$'\n''"))
            
                treedata = sg.TreeData()
                app_list = []
                i = 0
                for app in search_result:
                    if app != 'template':
                        app_list.append(app)
                        icon = '/home/pi/pi-apps/apps/' + app + '/icon-24.png'
                        treedata.insert('', i, ' ' + str(app), [], icon=icon)
                        
                        i += 1
                window['-APP LIST-'].update(treedata)
                window['-MENU BACK-'].update(visible=True)
            
            else: 
                if current_category != 'Category List':
                    show_category(current_category)

                elif current_category == 'Category List':
                    back_to_category_list()

        except:
            back_to_category_list()


    elif event == "-APP LIST-":  # An app was chosen from the list
        if window.Element('-APP LIST-').SelectedRows != []:
            current_app = app_list[window.Element('-APP LIST-').SelectedRows[0]]

        if current_app in app_categories:
            current_category = current_app
            if current_category != 'All Apps':
                category_apps = os.popen('cat /home/pi/pi-apps/etc/categories /home/pi/pi-apps/data/category-overrides | grep ' + current_category + ' | sed "s/|.*//g"').read().split('\n')
            else:
                category_apps = os.popen('/home/pi/pi-apps/api list_apps cpu_installable').read().split('\n')
            i = 0
            treedata = sg.TreeData()
            app_list = []
            i = 0
            for app in category_apps:
                if app != 'template':
                    app_list.append(app)
                    icon = '/home/pi/pi-apps/apps/' + app + '/icon-24.png'
                    treedata.insert('', i, ' ' + str(app), [], icon=icon)
                    
                    i += 1
            window['-APP LIST-'].update(treedata)
            window['-MENU BACK-'].update(visible=True)
        else:
            try:
                app = current_app
                load_app_info(app)

            except:
                pass

    elif event == '-DESCRIPTION-+FOCUS_IN+':
        widget = window['-DESCRIPTION-'].Widget
        widget.bind("<1>", widget.focus_set())
        window['-DESCRIPTION-'].update(disabled=True)
    elif event == '-DESCRIPTION-+FOCUS_OUT+':
        window['-DESCRIPTION-'].Widget.unbind("<1>")
        window['-DESCRIPTION-'].update(disabled=False)

    elif event == '-INSTALL BUTTON-':
        if current_app != '':
            app = current_app
            if os.popen('cat "/home/pi/pi-apps/data/status/' + app + '" 2>/dev/null').read().rstrip('\n') == 'uninstalled':
                os.popen('''/home/pi/pi-apps/etc/terminal-run '/home/pi/pi-apps/manage install "''' + app + '''"' ''').read()
            elif os.popen('cat "/home/pi/pi-apps/data/status/' + app + '" 2>/dev/null').read().rstrip('\n') == 'installed':
                os.popen('''/home/pi/pi-apps/etc/terminal-run '/home/pi/pi-apps/manage uninstall "''' + app + '''"' ''').read()
            load_app_info(app)
        else:
            pass

    elif event == '-WEBSITE_2-':
        webbrowser.open(window["-WEBSITE_2-"].get())

    elif event == '-WEBSITE_2-+MOUSE OVER+':
        window.set_cursor('hand2')

    elif event == '-WEBSITE_2-+MOUSE AWAY+':
        window.set_cursor('')
    
    elif event == '-MENU BACK-':
        back_to_category_list()
    
    elif event == '-APP LIST-+MOTION+':
        e = window['-APP LIST-'].user_bind_event
        region = window['-APP LIST-'].Widget.identify('region', e.x, e.y)
        if region == 'tree':
            col = 0
        elif region == 'cell':
            col = int(window['-APP LIST-'].Widget.identify_column(e.x)[1:])
        else:
            continue
        ids = window['-APP LIST-'].Widget.identify_row(e.y)
        key = window['-APP LIST-'].IdToKey[ids]
        if (key, col) != old_menu_index:
            first_line = ''
            app = treedata.tree_dict[key].text[1:]
            if app not in app_categories:
                with open('/home/pi/pi-apps/apps/' + app + '/description') as f:
                    first_lines = textwrap.wrap(f.readline(),60)
                    for line in first_lines:
                        first_line = first_line + line + '\n'
                window['-TOOLTIP-'].update(first_line)
                # window['-APP LIST-'].set_tooltip(tooltip_text=first_line)


            old_menu_index = (key, col)
    elif event == '-APP LIST-+MOUSE AWAY+':
        window['-TOOLTIP-'].update('')

    elif event == '-INSTALL-':
        if current_app != '' and current_app not in app_categories:
            app = current_app
            os.popen('''/home/pi/pi-apps/etc/terminal-run '
    source "/home/pi/pi-apps/api"
    generate_logo
    /home/pi/pi-apps/manage multi-install "''' + app + '''"
    if [ $? == 0 ];then
      echo
      #display countdown
      for i in {30..1} ;do
        echo -en "You can close this window now. Auto-closing in $i seconds.\e[0K\r"
        sleep 1
      done
    else
      echo -e "\nClose this window to exit."
      read enter 
    fi' ''').read()
            load_app_info(app)
        else:
            pass

    elif event == '-UNINSTALL-':
        print(current_app)
        if current_app != '' and current_app not in app_categories:
            app = current_app
            os.popen('''/home/pi/pi-apps/etc/terminal-run '
    source "/home/pi/pi-apps/api"
    generate_logo
    /home/pi/pi-apps/manage multi-uninstall "''' + app + '''"
    if [ $? == 0 ];then
      echo
      #display countdown
      for i in {30..1} ;do
        echo -en "You can close this window now. Auto-closing in $i seconds.\e[0K\r"
        sleep 1
      done
    else
      echo -e "\nClose this window to exit."
      read enter 
    fi' ''').read()
            load_app_info(app)
        else:
            pass

    elif event == '-CREDITS-':
        print('wow')
        print(current_app)
        if current_app != '':
            if current_app not in app_categories:
                app = current_app
                credits_text = os.popen('cat "/home/pi/pi-apps/apps/' + app + '/credits" 2>/dev/null').read().rstrip('\n')
                if credits_text != '':
                    sg.Window('Credits', [[sg.T(credits_text)], [sg.OK(s=10)]]).read(close=True)
                else:
                    sg.Window('Credits', [[sg.T('No credit found for ' + app + '.\n')], [sg.OK(s=10)]], size=(500, 100)).read(close=True)
            else:
                pass #category is selected, no credits available, skip
        else:
            pass

    elif event == '-SCRIPTS-':
        print('wow')
        if current_app != '':
            if current_app not in app_categories:
                app = current_app
                for file in ['install', 'install-32', 'install-64', 'uninstall']:
                    if exists('/home/pi/pi-apps/apps/' + app + '/' + file):
                        os.popen('/home/pi/pi-apps/api text_editor "/home/pi/pi-apps/apps/' + app + '/' + file + '"')
            else:
                pass #category is selected
        else:
            pass
    
window.close()
