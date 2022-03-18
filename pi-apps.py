#!/usr/bin/env python3

# Import modules
import time
import sys
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

def debug(message):
    if enable_debug == True:
        print(message)
    else:
        pass


def install_app(app):
    window.Hide()
    debug('Installing ' + app + '.')
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
    debug('Done installing ' + app + '.')
    window.UnHide()
    window.TKroot.focus_force()



def uninstall_app(app):
    window.Hide()
    debug('Uninstalling ' + app + '.')
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
    debug('Done uninstalling ' + app + '.')
    window.UnHide()
    window.TKroot.focus_force()


def back_to_category_list():
    global app_list
    global current_category
    global app_list_data
    debug('Returning to Category List.')
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
    debug('Done returning Category List')


def show_category(category):
    global app_list_data
    global app_list
    global current_category
    global current_app
    if category == 'All Apps':
        debug('\nShowing All Apps category.')
        category_apps = os.popen(
            f'{DIRECTORY}/api list_apps cpu_installable | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps visible)" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps cpu_installable)"').read().split('\n')

    elif category == 'Installed':
        debug('\nShowing Installed category.')
        category_apps = os.popen(
            f'{DIRECTORY}/api list_apps installed').read().split('\n')

    else:  # Other categories
        debug('\nShowing ' + category + ' category.')
        category_apps = os.popen(
            f'cat {DIRECTORY}/etc/categories  {DIRECTORY}/data/category-overrides 2>/dev/null | grep {category} | sed "s/|.*//g" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps visible)" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps cpu_installable)"').read().split('\n')

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
    current_app = ''
    window['-MENU BACK-'].update(visible=True)
    window['-SEARCH BAR-'].update('')
    window['-TOOLTIP-'].update('')
    current_category = category
    debug('Done showing ' + category + ' category.')


def load_app_info(app):
    global status_text
    global website_text
    global current_app
    global description_text
    global button_list

    debug('\nLoading ' + app + ' info.')
    status_text = os.popen(
        f'{DIRECTORY}/api app_status "' + app + '" 2>/dev/null').read().rstrip('\n')
    if status_text == '':
        status_text = 'uninstalled'
    debug(app + "'s status: " + status_text)
    website_text_original = textwrap.wrap(os.popen(f'cat "{DIRECTORY}/apps/' +
                                                   app + '/website" 2>/dev/null').read().rstrip('\n'), 75, replace_whitespace=False)
    website_text = ''
    if website_text_original != []:
        if len(website_text_original) > 1:
            for line in website_text_original:
                website_text += line + '\n'
        else:
            website_text = website_text_original[0]
        debug(app + "'s website: " + website_text)

    description_text = os.popen(f'cat "{DIRECTORY}/apps/' +
                                app + '/description"').read()
    debug(app + "'s description: \n" + description_text)

    users_count = int(''.join(filter(str.isdigit, os.popen(f"{DIRECTORY}/api usercount '{app}' 2>/dev/null").read().rstrip('\n'))))
    debug(app + "'s users count: " + str(users_count))

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

    debug('Loading buttons.')
    buttons = ['-BUTTON 1-', '-BUTTON 2-', '-BUTTON 3-',
               '-BUTTON 4-', '-BUTTON 5-', '-BUTTON 6-']

    for button in buttons:
        window[button].update(' ', visible=False, image_filename='')

    button_list = []
    i = []

    if status_text == 'installed':
        # uninstall button
        i.append('uninstall')
        # credits
        if os.path.exists(f'{DIRECTORY}/apps/{app}/credits'):
            i.append('credits')
        # scripts
        if os.popen(f'{DIRECTORY}/api app_type ' + app).read().strip('\n') != 'package':
            i.append('scripts')
        # edit
        if show_edit_button is True:
            i.append('edit')

    elif status_text == 'uninstalled':
        # install button
        i.append('install')
        # credits
        if os.path.exists(f'{DIRECTORY}/apps/{app}/credits'):
            i.append('credits')
        # scripts
        if os.popen(f'{DIRECTORY}/api app_type ' + app).read().strip('\n') != 'package':
            i.append('scripts')
        # edit
        if show_edit_button is True:
            i.append('edit')

    elif status_text == 'corrupted':
        i.append('install')
        i.append('uninstall')
        # credits
        if os.path.exists(f'{DIRECTORY}/apps/{app}/credits'):
            i.append('credits')
        # scripts
        if os.popen(f'{DIRECTORY}/api app_type ' + app).read().strip('\n') != 'package':
            i.append('scripts')
        # edit
        if show_edit_button is True:
            i.append('edit')
        i.append('errors')

    n = 0

    for button in i:
        if button == 'install':
            window[buttons[n]].update(
                '      ', visible=True, image_filename=f'{DIRECTORY}/icons/install.png', )
            window[buttons[n]].set_tooltip('Install ' + app)

            button_list.append('install')
        elif button == 'uninstall':
            window[buttons[n]].update(
                '  ', visible=True, image_filename=f'{DIRECTORY}/icons/uninstall.png', )
            button_list.append('uninstall')
            window[buttons[n]].set_tooltip('Uninstall' + app)
        elif button == 'credits':
            window[buttons[n]].update("Credits", visible=True)
            window[buttons[n]].set_tooltip(
                'See who made the app and who put it on Pi-Apps')
            button_list.append('credits')
        elif button == 'scripts':
            window[buttons[n]].update(
                '  ', visible=True, image_filename=f'{DIRECTORY}/icons/shellscript.png',)
            window[buttons[n]].set_tooltip(
                "Feel free to see how an app is installed or uninstalled!\nPerfect for learning or troubleshooting.")
            button_list.append('scripts')
        elif button == 'edit':
            window[buttons[n]].update(
                visible=True, image_filename=f'{DIRECTORY}/icons/edit.png', )
            window[buttons[n]].set_size((0, 24))
            print(type(window))
            button_list.append('edit')
            window[buttons[n]].set_tooltip('Make changes to the app')
        elif button == 'errors':
            window[buttons[n]].update(
                visible=True, image_filename=f'{DIRECTORY}/icons/log-file.png')
            window[buttons[n]].set_tooltip('')
            button_list.append('errors')

        debug('Added ' + button + ' button in ' + buttons[n])
        n += 1

    debug('Done loading buttons.')
    debug('Done loading ' + app + '.')
    current_app = app


# Initialize configs

if '--debug' in sys.argv:
    enable_debug = True
else:
    enable_debug = False

if "DIRECTORY" not in os.environ:
    if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/api') is True:
        DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    else:
        DIRECTORY = os.getenv('HOME') + '/pi-apps'
else:
    DIRECTORY = os.getenv("DIRECTORY")

debug('DIRECTORY: ' + DIRECTORY)


# Settings

os.spawnl(os.P_NOWAIT, f'"{DIRECTORY}/updater"', 'set-status', '&>/dev/null')

try:
    with open(f'{DIRECTORY}/data/settings/Shuffle App list', 'r') as f:
        if f.read().replace('\n', '') == 'Yes':
            shuffle_app_list = True
        else:
            shuffle_app_list = False
except:
    shuffle_app_list = False

debug('Shuffle app list: ' + str(shuffle_app_list))

try:
    with open(f'{DIRECTORY}/data/settings/Show Edit button', 'r') as f:
        if f.read().replace('\n', '') == 'Yes':
            show_edit_button = True
        else:
            show_edit_button = False
except:
    show_edit_button = False

debug('Show edit button: ' + str(show_edit_button))

font = Gtk.Settings.get_default().get_property("gtk-font-name")
default_font_name = font.split(',')[0].replace(' ', '')
default_font_size = font[-2:]
default_font = default_font_name + ' ' + default_font_size
debug('Font: ' + default_font)

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
debug('Categories: ' + str(app_categories))

app_list = []
i = 0
app_list_data = sg.TreeData()
for category in sorted(app_categories):
    app_list.append(category)
    icon = f'{DIRECTORY}/icons/categories/' + category + '.png'
    app_list_data.insert('', i, ' ' + str(category), [], icon=icon)
    i += 1
current_category = 'Category List'



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
        sg.In(size=(25, 1), enable_events=True,
              font=default_font, key='-SEARCH BAR-'),
        sg.Button("Search", font=default_font,
                  key='-SEARCH-', bind_return_key=True),
    ],
    [
        sg.Text('')
    ],
    [
        sg.Column([[sg.Text('', key='-TOOLTIP-', size=(65, 6))]], pad=(0, 0))
    ],
    [
        sg.Tree(app_list_data, headings='', num_rows=12,
                select_mode='browse', enable_events=True, key='-APP LIST-', font=default_font, col0_width=45, row_height=30, auto_size_columns=False),
    ],
    [
        sg.pin(sg.Button(key='-MENU BACK-',
               image_filename=f'{DIRECTORY}/icons/back.png', button_text=' ', visible=False, tooltip='Return to category list')),
        sg.Column([[sg.Button(key='-UPDATES-',
               image_filename=f'{DIRECTORY}/icons/categories/Updates.png', button_text=' ', visible=False, tooltip='View updatable apps')]], element_justification='r', expand_x=True),
    ],
]

app_info_column = [
    [sg.Image(key='-APP ICON-', filename=f'{DIRECTORY}/icons/proglogo.png'),
     sg.Text("", key="-APP NAME-", font=default_font_name + " 14"), sg.Button(key="-GITHUB BUTTON-",
                                                                              image_filename=f'{DIRECTORY}/icons/github.png', button_text="             ", tooltip='View Pi-Apps GitHub page'),  
     sg.Button(key="-WEBSITE BUTTON-", image_filename=f'{DIRECTORY}/icons/website.png', button_text="             ", tooltip='View Pi-Apps website')],
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

    [sg.Column([[sg.Button(key="-BUTTON 1-", font=default_font,
               image_filename=f'{DIRECTORY}/icons/shellscript.png', button_text="Credits", visible=False)]], pad=(0, 0)),
     sg.Column([[sg.Button(key="-BUTTON 2-", font=default_font,
               button_text='   ', image_filename=f'{DIRECTORY}/icons/shellscript.png', visible=False,)]]),
     sg.Column([[sg.Button(key="-BUTTON 3-", font=default_font,  tooltip="Errors", button_text='   ',
               image_filename=f'{DIRECTORY}/icons/shellscript.png', visible=False,)]]),
     sg.Column([[sg.Button(key="-BUTTON 4-", font=default_font,
               image_filename=f'{DIRECTORY}/icons/shellscript.png', visible=False)]], pad=(0, 0)),
     sg.Column([[sg.Button(key="-BUTTON 5-", font=default_font,
               image_filename=f'{DIRECTORY}/icons/shellscript.png', visible=False)]], pad=(0, 0)),
     sg.Column([[sg.Button(key="-BUTTON 6-", font=default_font,
               image_filename=f'{DIRECTORY}/icons/shellscript.png', visible=False)]], pad=(0, 0)),

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
window.TKroot.focus_force()

if os.popen(f'if {DIRECTORY}/updater get-status 2>/dev/null; then echo 0; else echo 1; fi').read().rstrip('\n') == '0':
    window['-UPDATES-'].update(visible=True)
else:
    window['-UPDATES-'].update(visible=False)
    

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

        if current_app == '':
            pass
        elif current_app in app_categories:  # If the item is a category, enter the category
            current_category = current_app
            show_category(current_category)
        elif current_app in os.popen(
                f'{DIRECTORY}/api list_apps cpu_installable | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps visible)" | {DIRECTORY}/api list_intersect "$({DIRECTORY}/api list_apps cpu_installable)"').read().split('\n'):
            # try:
            app = current_app
            load_app_info(app)

            # except:
            #     pass

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

    elif event == '-BUTTON 1-' or event == '-BUTTON 2-' or event == '-BUTTON 3-' or event == '-BUTTON 4-' or event == '-BUTTON 5-' or event == '-BUTTON 6-':
        operation = button_list[int(
            ''.join([n for n in event if n.isdigit()])) - 1]

        if operation == 'install':
            if current_app != '' and current_app not in app_categories:
                app = current_app
                install_app(app)
                load_app_info(app)
            else:
                pass
        elif operation == 'uninstall':
            if current_app != '' and current_app not in app_categories:
                app = current_app
                uninstall_app(app)
                load_app_info(app)
            else:
                pass
        elif operation == 'credits':
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
        elif operation == 'scripts':
            if current_app != '':
                if current_app not in app_categories:
                    app = current_app
                    if os.popen(f'{DIRECTORY}/api app_type ' + app).read().strip('\n') != 'package':
                        for file in ['install', 'install-32', 'install-64', 'uninstall']:
                            if os.path.exists(f'{DIRECTORY}/apps/' + app + '/' + file):
                                os.popen(
                                    f'{DIRECTORY}/api text_editor "{DIRECTORY}/apps/' + app + '/' + file + '"')
                                time.sleep(0.1)
                    else:
                        sg.Window('No scripts found', [[sg.T(
                            app + ' is a package app.\n')], [sg.OK(s=10)]], size=(500, 100)).read(close=True)

                else:
                    pass  # category is selected
            else:
                pass
        elif operation == 'errors':
            if current_app != '':
                app = current_app
                print(app)
                error_file = os.popen(
                    f'ls "{DIRECTORY}/logs"/* -t | grep "fail-' + app + '" | head -n1').read()
                os.popen(f'{DIRECTORY}/api text_editor ' + error_file)

    elif event == '-GO TO SEARCH-':  # When alt+s is pressed, focus to search bar
        window.TKroot.focus_force()

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

    elif event == '-UPDATES-':
        window.Hide()
        os.popen(f'"{DIRECTORY}/updater" gui fast').read()
        window.UnHide()
        if os.popen(f'if {DIRECTORY}/updater get-status 2>/dev/null; then echo 0; else echo 1; fi').read().rstrip('\n') == '0':
            window['-UPDATES-'].update(visible=True)
        else:
            window['-UPDATES-'].update(visible=False)
        window.TKroot.focus_force()

window.close()
