#!/usr/bin/env python3

# Import modules
import random
import textwrap
import webbrowser
import os
import os.path
import PySimpleGUI as sg
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


# Define functions

def install_app(app):
    window.Hide()
    os.popen(f'''{DIRECTORY}/etc/terminal-run '
    DIRECTORY={DIRECTORY}
    source "{DIRECTORY}/api"
    generate_logo
    {DIRECTORY}/manage multi-install "''' + app + '''"
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
    fi' 'Installing ''' + app + '''' ''').read()
    window.UnHide()


def uninstall_app(app):
    window.Hide()
    os.popen(f'''{DIRECTORY}/etc/terminal-run '
    DIRECTORY={DIRECTORY}
    source "{DIRECTORY}/api"
    generate_logo
    {DIRECTORY}/manage multi-uninstall "''' + app + '''"
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
    fi' 'Unnstalling ''' + app + '''' ''').read()
    window.UnHide()


def back_to_category_list():
    global app_list
    global current_category
    global app_list_data
    app_list = []
    i = 0
    app_list_data = sg.TreeData()
    for category in sorted(app_categories):
        app_list.append(category)
        icon = f'{DIRECTORY}/icons/categories/' + category + '.png'
        app_list_data.insert('', i, ' ' + str(category), [], icon=icon)
        i += 1

    window['-APP LIST-'].update(app_list_data)
    window['-MENU BACK-'].update(visible=False)
    window['-TOOLTIP-'].update('')
    window['-SEARCH BAR-'].update('')

    current_category = 'Category List'


def show_category(category):
    global app_list_data
    global app_list
    global current_category
    if category == 'All Apps':
        category_apps = os.popen(
            f'{DIRECTORY}/api list_apps cpu_installable | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps visible)" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps cpu_installable)"').read().split('\n')

    elif category == 'Installed':
        category_apps = os.popen(
            f'{DIRECTORY}/api list_apps installed').read().split('\n')

    else:  # Other categories
        category_apps = os.popen(
            f'cat  {DIRECTORY}/etc/categories  {DIRECTORY}/data/category-overrides 2>/dev/null | grep {category} | sed "s/|.*//g" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps visible)" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps cpu_installable)"').read().split('\n')

    i = 0
    app_list_data = sg.TreeData()
    app_list = []

    if shuffle_app_list == True:
        random.shuffle(category_apps)

    for app in category_apps:
        if app != 'template':
            app_list.append(app)
            icon = f'{DIRECTORY}/apps/' + app + '/icon-24.png'
            app_list_data.insert('', i, ' ' + str(app), [], icon=icon)
            i += 1

    window['-APP LIST-'].update(app_list_data)
    window['-MENU BACK-'].update(visible=True)
    window['-SEARCH BAR-'].update('')
    window['-TOOLTIP-'].update(first_line)
    current_category = category


def load_app_info(app):
    global status_text
    global website_text
    global current_app
    global description_text
    status_text = os.popen(
        f'{DIRECTORY}/api app_status "' + app + '"').read().rstrip('\n')
    if status_text == '':
        status_text = 'uninstalled'
    website_text_original = textwrap.wrap(os.popen(f'cat "{DIRECTORY}/apps/' +
                                                   app + '/website" 2>/dev/null').read().rstrip('\n'), 75, replace_whitespace=False)
    website_text = ''
    if website_text_original != []:
        if len(website_text_original) > 1:
            for line in website_text_original:
                website_text += line + '\n'
        else:
            website_text = website_text_original[0]

    description_text = os.popen(f'cat "{DIRECTORY}/apps/' +
                                app + '/description"').read()

    users_count = int(
        os.popen(f"{DIRECTORY}/api usercount '{app}' 2>/dev/null").read().rstrip('\n'))

    window["-APP NAME-"].update(app,
                                font=default_font_name + ' ' + str(20) + ' bold')
    window["-APP ICON-"].update(
        filename=f'{DIRECTORY}/apps/' + app + '/icon-64.png')
    window["-STATUS-"].update("Status:   " + status_text)
    if website_text != '':
        window["-WEBSITE_1-"].update("Website:")
        window["-WEBSITE_2-"].update(website_text)
    else:
        window["-WEBSITE_1-"].update("")
        window["-WEBSITE_2-"].update('')

    if users_count != '':
        window["-USERS_1-"].update(' ' + str(users_count))
        if users_count >= 1500 and users_count < 10000:
            window["-USERS_2-"].update('users!')
        elif users_count >= 10000:
            window["-USERS_2-"].update('users!!')
        elif users_count > 1:
            window["-USERS_2-"].update('users')
        else:
            window["-USERS-"].update("user")

    window["-GITHUB BUTTON-"].update(visible=False)
    window["-WEBSITE BUTTON-"].update(visible=False)
    window["-DESCRIPTION-"].update(description_text)
    if os.popen(f'{DIRECTORY}/api app_type ' + app).read().strip('\n') != 'package':
        window["-SCRIPTS-"].update(visible=True)
    else:
        window["-SCRIPTS-"].update(visible=False)
    window["-CREDITS-"].update(visible=True)
    window["-UNINSTALL-"].update(visible=False)
    window["-ERRORS-"].update(visible=True)
    window["-ERRORS-"].update(visible=False)

    if status_text == 'corrupted':
        window["-ERRORS-"].update(visible=True)
        window["-INSTALL OR UNINSTALL-"].update(
            visible=True, image_filename=f'{DIRECTORY}/icons/install.png')
        window["-UNINSTALL-"].update(visible=True,
                                     image_filename=f'{DIRECTORY}/icons/uninstall.png')
    elif status_text == 'uninstalled':
        window["-INSTALL OR UNINSTALL-"].update(
            visible=True, image_filename=f'{DIRECTORY}/icons/install.png')
    elif status_text == 'installed':
        window["-INSTALL OR UNINSTALL-"].update(
            visible=True, image_filename=f'{DIRECTORY}/icons/uninstall.png')
    current_app = app


# Initialize configs
if "DIRECTORY" not in os.environ:
    if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/api') is True:
        DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    else:
        DIRECTORY = '/home/pi/pi-apps'
else:
    DIRECTORY = os.getenv("DIRECTORY")

apps = []

for app in sorted(os.listdir(f'{DIRECTORY}/apps')):
    if app != 'template':
        apps.append(app)

# Settings

try:
    with open(f'{DIRECTORY}/data/settings/Shuffle App list', 'r') as f:
        if f.read().replace('\n', '') == 'Yes':
            shuffle_app_list = True
        else:
            shuffle_app_list = False
except:
    shuffle_app_list = False


try:
    with open(f'{DIRECTORY}/data/settings/Show Edit button', 'r') as f:
        if f.read().replace('\n', '') == 'Yes':
            show_edit_button = True
        elif f.read().replace('\n', '') == 'No':
            show_edit_button = False
except:
    show_edit_button = False

font = Gtk.Settings.get_default().get_property("gtk-font-name")
default_font_name = font.split(',')[0].replace(' ', '')
default_font_size = font[-2:]
default_font = default_font_name + ' ' + default_font_size
old_list_index = (None, None)
current_app = ''

app_categories = [
    'All Apps',
    'Imported',
    'Installed',
    'Tools',
    'Games',
    'Internet',
    'Editors',
    'Multimedia',
    'Browsers',
    'Appearance',
]


app_list = []
i = 0
app_list_data = sg.TreeData()
for category in sorted(app_categories):
    app_list.append(category)
    icon = f'{DIRECTORY}/icons/categories/' + category + '.png'
    app_list_data.insert('', i, ' ' + str(category), [], icon=icon)
    i += 1
current_category = 'Category List'

github_image = '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'


# Create column layouts
search_column = [
    [
        sg.Image(filename=f'{DIRECTORY}/icons/proglogo.png', size=(400, 120))
    ],
    [
        sg.Text('')
    ],
    [
        sg.Text("Search apps: ", font=default_font),
        sg.In(size=(25, 1), enable_events=True, font=default_font, key='-SEARCH BAR-'),
        sg.Button("Search", font=default_font, key='-SEARCH-', bind_return_key=True),
    ],
    [
        sg.Text('')
    ],
    [
        sg.Column([[sg.Text('', key='-TOOLTIP-', size=(65, 6))]], pad=(0, 0))
    ],
    [
        sg.Tree(app_list_data, headings='', num_rows=12,
                select_mode='browse', enable_events=True, key='-APP LIST-', font=default_font, col0_width=40, row_height=30, auto_size_columns=False),
    ],
    [
        sg.Button(key='-MENU BACK-',
                  image_filename=f'{DIRECTORY}/icons/back.png', button_text=' ', visible=False)
    ],
]

app_info_column = [
    [sg.Image(key='-APP ICON-', filename=f'{DIRECTORY}/icons/proglogo.png'),
     sg.Text("", key="-APP NAME-", font=default_font_name + " 14"), sg.Button(key="-GITHUB BUTTON-",
                                                                              image_filename=f'{DIRECTORY}/icons/github.png', button_text="             "),  sg.Button(key="-WEBSITE BUTTON-",
                                                                                                                                                                       image_filename=f'{DIRECTORY}/icons/website.png', button_text="             ")],
    [sg.Text("""The most popular app store for Raspberry Pi computers.""",
             key="-STATUS-", font=default_font)],
    [sg.Text(key="-WEBSITE_1-", font=default_font), sg.Text(key="-WEBSITE_2-",
                                                            click_submits=True, text_color='blue', font=default_font + ' underline')],
    [sg.Text(key="-USERS_1-", font=default_font + ' bold', pad=(0, 0)),
     sg.Text(key="-USERS_2-", font=default_font, pad=(0, 0))],

    [sg.Multiline("""Let's be honest: Linux is harder to master than Windows. 
Sometimes it's not user-friendly, and following an outdated tutorial may break your Raspberry Pi's operating system.
There is no centralized software repository, except for the apt repositories which lack many desktop applications.
Surely there is a better way! There is.
Introducing Pi-Apps, a well-maintained collection of app installation-scripts that you can run with one click.

Pi-Apps now serves over 1,000,000 people and hosts nearly 200 apps.""", key="-DESCRIPTION-", size=(75, 20), font=default_font)],

    [sg.Column([[sg.Button(key="-CREDITS-",
               button_text="Credits", font=default_font, tooltip='See who made the app and who put it on Pi-Apps', visible=False)]], pad=(0, 0)),
     sg.Column([[sg.Button(key="-SCRIPTS-",
               tooltip="Feel free to see how an app is installed or uninstalled!\nPerfect for learning or troubleshooting.", button_text='   ', image_filename=f'{DIRECTORY}/icons/shellscript.png', font=default_font, visible=False,)]]),
     sg.Column([[sg.Button(key="-ERRORS-", tooltip="Errors", button_text='   ',
               image_filename=f'{DIRECTORY}/icons/log-file.png', font=default_font, visible=False,)]]),
     sg.Text('',pad=(50, 0)),
     sg.Column([[sg.Button(key="-UNINSTALL-",
               image_filename=f'{DIRECTORY}/icons/uninstall.png', button_text="  ", visible=False)]]),
     sg.Column([[sg.Button(key="-INSTALL OR UNINSTALL-",
               image_filename=f'{DIRECTORY}/icons/install.png', button_text="  ", visible=False)]]),
     ]
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
                   icon=f'{DIRECTORY}/icons/logo.png', finalize=True, size=(1250, 800))


# https://stackoverflow.com/questions/38871450/how-can-i-get-the-default-colors-in-gtk

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
window.bind('<Alt-s>', '-GO TO SEARCH-')
window['-SEARCH BAR-'].set_focus()


# Run the Event Loop
while True:
    # Reset variables
    event, values = window.read()
    app = ''
    search_query = ''
    search_result = ''
    f = ''
    i = None

    # Exit
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-SEARCH-":
        search_query = values["-SEARCH BAR-"]
        search_result = []
        try:
            if search_query != '':  # If search query is not empty
                output = os.popen(f'{DIRECTORY}/api list_apps cpu_installable | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps visible)" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps cpu_installable)" | grep -i "' +
                                  search_query + '" | sort').read()

                # Create temporary file to store search results
                temp_file = os.popen('mktemp').read().strip('\n')
                f = open(temp_file, 'w')
                f.write(output)
                f.close()
                f = open(temp_file, 'r')

                for line in sorted(f.readlines()):
                    if line != '\n':
                        search_result.append(line.strip("'$'\n''"))

                f.close()

                # Create new app_list_data
                app_list_data = sg.TreeData()
                app_list = []
                i = 0
                for app in search_result:
                    if app != 'template':
                        app_list.append(app)
                        icon = f'{DIRECTORY}/apps/' + app + '/icon-24.png'
                        app_list_data.insert(
                            '', i, ' ' + str(app), [], icon=icon)
                        i += 1

                # Update to the app_list_data generated just now
                window['-APP LIST-'].update(app_list_data)
                # Make back button visible so users can return to category list
                window['-MENU BACK-'].update(visible=True)

                ids = window['-APP LIST-'].Widget.identify_row(1)
                key = window['-APP LIST-'].IdToKey[ids]
                window['-APP LIST-'].Widget.selection_set(ids)
                
                window['-APP LIST-'].set_focus()

            else:  # search query is empty, back to category
                if current_category != 'Category List':
                    show_category(current_category)

                elif current_category == 'Category List':
                    back_to_category_list()

        except:  # If anything goes wrong, back to category list
            back_to_category_list()

    elif event == "-APP LIST-":  # An app was chosen from the list

        # Get current selected item
        if window.Element('-APP LIST-').SelectedRows != []:
            current_app = app_list[window.Element(
                '-APP LIST-').SelectedRows[0]]

        if current_app in app_categories:  # If the item is a category, enter the category
            current_category = current_app
            show_category(current_category)
        else:
            try:
                app = current_app
                load_app_info(app)

            except:
                pass

    elif event == '-DESCRIPTION-+FOCUS_IN+':  # When focus in description box, remove caret
        window['-DESCRIPTION-'].Widget.bind("<1>",
                                            window['-DESCRIPTION-'].Widget.focus_set())
        window['-DESCRIPTION-'].update(disabled=True)

    elif event == '-DESCRIPTION-+FOCUS_OUT+':
        window['-DESCRIPTION-'].Widget.unbind("<1>")
        window['-DESCRIPTION-'].update(disabled=False)

    elif event == '-INSTALL OR UNINSTALL-':
        if current_app != '':
            app = current_app
            if status_text == 'uninstalled':
                install_app(app)
            else:
                uninstall_app(app)

            load_app_info(app)
        else:
            pass

    elif event == '-WEBSITE_2-':  # When clicked on website URL, open in browser
        webbrowser.open(window["-WEBSITE_2-"].get())

    elif event == '-WEBSITE_2-+MOUSE OVER+':  # When hover on website URL, set cursor to URL cursor
        window.set_cursor('hand2')

    elif event == '-WEBSITE_2-+MOUSE AWAY+':  # When mouse leave website URL, reset cursor
        window.set_cursor('')

    elif event == '-MENU BACK-':  # When clicked on back button, return to category list
        back_to_category_list()

    elif event == '-APP LIST-+MOTION+':  # When mouse is in app list, detect what entry and show tooltip
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
        if (key, col) != old_list_index:
            first_line = ''
            app = app_list_data.tree_dict[key].text[1:]
            if app not in app_categories:
                with open(f'{DIRECTORY}/apps/' + app + '/description') as f:
                    first_line = textwrap.fill(f.readline(), 70)
                window['-TOOLTIP-'].update(first_line)
                # window['-APP LIST-'].set_tooltip(tooltip_text=first_line)

            old_list_index = (key, col)

    elif event == '-APP LIST-+MOUSE AWAY+':  # When mouse leave app list, clear tooltips
        window['-TOOLTIP-'].update('')

    elif event == '-INSTALL-':
        if current_app != '' and current_app not in app_categories:
            app = current_app
            install_app(app)
            load_app_info(app)
        else:
            pass

    elif event == '-UNINSTALL-':
        if current_app != '' and current_app not in app_categories:
            app = current_app
            uninstall_app(app)
            load_app_info(app)
        else:
            pass

    elif event == '-CREDITS-':  # Popup window
        if current_app != '':
            if current_app not in app_categories:
                app = current_app
                credits_text = os.popen(
                    f'cat "{DIRECTORY}/apps/' + app + '/credits" 2>/dev/null').read().rstrip('\n')
                if credits_text != '':
                    sg.Window('Credits', [[sg.T(credits_text)], [
                              sg.OK(s=10)]]).read(close=True)
                else:
                    sg.Window('Credits', [
                              [sg.T('No credit found for ' + app + '.\n')], [sg.OK(s=10)]]).read(close=True)
            else:
                pass  # category is selected, no credits available, skip
        else:
            pass

    elif event == '-SCRIPTS-':
        if current_app != '':
            if current_app not in app_categories:
                app = current_app
                if os.popen(f'{DIRECTORY}/api app_type ' + app).read().strip('\n') != 'package':
                    for file in ['install', 'install-32', 'install-64', 'uninstall']:
                        if os.path.exists(f'{DIRECTORY}/apps/' + app + '/' + file):
                            os.popen(
                                f'{DIRECTORY}/api text_editor "{DIRECTORY}/apps/' + app + '/' + file + '"')
                else:
                    sg.Window('No scripts found', [[sg.T(
                        app + ' is a package app.\n')], [sg.OK(s=10)]], size=(500, 100)).read(close=True)

            else:
                pass  # category is selected
        else:
            pass

    elif event == '-GO TO SEARCH-':  # When alt+s is pressed, focus to search bar
        window['-SEARCH BAR-'].set_focus()

    elif event == '-ERRORS-':  # Show error report
        if current_app != '':
            app = current_app
            print(app)
            error_file = os.popen(
                f'ls "{DIRECTORY}/logs"/* -t | grep "fail-' + app + '" | head -n1').read()
            os.popen(f'{DIRECTORY}/api text_editor ' + error_file)

    elif event == '-GITHUB BUTTON-':
        webbrowser.open('https://github.com/Botspot/pi-apps')

    elif event == '-WEBSITE BUTTON-':
        webbrowser.open('https://pi-apps.io')

    elif event == '-CLEAR SEARCH-':
        if current_category != 'Category List':
            show_category(current_category)

        elif current_category == 'Category List':
            back_to_category_list()

    elif event == '-REFRESH-':  # Refresh
        if current_category != 'Category List':
            show_category(current_category)
        elif current_category == 'Category List':
            back_to_category_list()

        if current_app != '':
            load_app_info(current_app)


window.close()
