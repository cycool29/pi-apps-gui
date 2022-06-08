# pi-apps-gui

A Python version of [Pi-Apps](https://github.com/Botspot/pi-apps) GUI built with PySimpleGUI, with some unique features. 


## Install

To replace it with Pi-Apps default GUI:
```bash
sudo apt install python3-tk
pip3 install PySimpleGUI
cd ~/pi-apps
rm -f gui 
wget https://github.com/cycool29/pi-apps-gui/raw/master/github.png -O icons/github.png
wget https://github.com/cycool29/pi-apps-gui/raw/master/website.png -O icons/website.png
wget https://github.com/cycool29/pi-apps-gui/raw/master/pi-apps.py -O gui
chmod +x ./gui
```

## Uninstall 

To change back to Pi-Apps default GUI:
```bash
cd ~/pi-apps
rm -f gui icons/github.png icons/website.png
wget https://github.com/Botspot/pi-apps/raw/master/gui -O gui
chmod +x ./gui
```

## Features

- **Portable Search Function** - easily search for apps in the search bar, or with pressing <kbd>Alt</kbd> + <kbd>S</kbd>.
- **Keyboard Shortcuts** - without using your mouse, you can:
  - **Install Selected App** by pressing <kbd>Ctrl</kbd> + <kbd>I</kbd>
  - **Uninstall Selected App** by pressing <kbd>Ctrl</kbd> + <kbd>U</kbd>
  - **Refresh App List and App Info** by pressing <kbd>Ctrl</kbd> + <kbd>R</kbd>
  - **View App Scripts** by pressing <kbd>Ctrl</kbd> + <kbd>S</kbd>
  - **View App Credits** by pressing <kbd>Ctrl</kbd> + <kbd>C</kbd>
  - **Search Apps** by pressing <kbd>Alt</kbd> + <kbd>S</kbd>
- **Dual-pane Layout in a Window** - the app info tab and app list tab are in one window, so loading categories and apps are a little bit faster.

## To-do
- [ ] Add theme selection
- [ ] Make tray icon
- [ ] Write another settings for toggling features (theme, tray icon, etc...)
- [ ] Announcement text label
- [x] Fix app info tab change its size when changing category
- [ ] Support multi-installing
- [ ] Try to add install/uninstall buttons on app list for power users 

## Suggestions

Suggestions or PRs are **very very very welcome**, as I am now lack of new ideas for features. :(

You can submit suggestions by opening a new issue.

## Screenshots

![image](https://user-images.githubusercontent.com/88134003/169481515-a16342bc-b1fa-4469-aa78-5eeca37af043.png)

![image](https://user-images.githubusercontent.com/88134003/169481702-e2e7ee15-ccb9-497d-bcc3-b63d7e14e2c1.png)



## Credits 

[Pi-Apps](https://github.com/Botspot/pi-apps) is an open source project developed by [Botspot](https://github.com/Botspot).
I am just creating another GUI for it.

## License

This project is licensed under the GNU General Public License v3.0. See the [COPYING](COPYING) file for more info.


