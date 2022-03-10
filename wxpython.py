import webbrowser
import os
import subprocess
import wx


class window(wx.Frame):

    def __init__(self, parent, title):
        super(window, self).__init__(parent, title=title, size=(900, 300))

        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(
            wx.Bitmap("/home/pi/pi-apps/icons/logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        panel = wx.Panel(self)
        box_horizontal = wx.BoxSizer(wx.HORIZONTAL)
        box_vertical = wx.BoxSizer(wx.VERTICAL)

        apps = []

        for app in sorted(os.listdir('/home/pi/pi-apps/apps')):
            if app != 'template':
                apps.append(app)

        self.list = wx.ListBox(panel, size=(200, -1),
                               choices=apps, style=wx.LB_SINGLE)

        self.app_description = wx.TextCtrl(panel, size=(
            500, 300), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.TE_RICH)
        
        install_icon = wx.Bitmap('/home/pi/pi-apps/icons/install.png')
        self.install_button = wx.Button(panel, label="", size=(50, -1))
        self.install_button.SetBitmap(install_icon)
        uninstall_icon = wx.Bitmap('/home/pi/pi-apps/icons/uninstall.png')
        self.uninstall_button = wx.Button(panel, label="", size=(50, -1))
        self.uninstall_button.SetBitmap(uninstall_icon)

        box_horizontal.Add(self.list, 0, wx.EXPAND)
        box_horizontal.Add(self.app_description, 2)
        box_horizontal.Add(self.install_button, wx.EXPAND)
        box_horizontal.Add(self.uninstall_button, wx.EXPAND)

        panel.SetSizer(box_horizontal)
        # panel.SetSizer(box_vertical)
        panel.Fit()

        self.Bind(wx.EVT_LISTBOX, self.onListBox, self.list)
        self.Bind(wx.EVT_BUTTON, self.install_app, self.install_button)
        self.app_description.Bind(wx.EVT_TEXT_URL, self.open_link)
        self.app_description.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
        # self.app_description.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Show(True)

    def open_link(self, event):
        if event.MouseEvent.LeftUp():
            ## print('OnTextURL LeftUp %s' % url)
            url = self.app_description.GetRange(event.GetURLStart(), event.GetURLEnd())
            webbrowser.open_new_tab(url)
        event.Skip()


    def install_app(self, event):
        app = self.list.GetString(self.list.GetSelection())
        subprocess.Popen(['/home/pi/pi-apps/manage', 'install', app])
        

    def OnMouseEvent(self, event):
        if event.Moving():
            self.app_description.SetCursor(wx.STANDARD_CURSOR)

    # def OnSetFocus(self, event):
    #     self.Navigate(wx.NavigationKeyEvent.IsForward)

    def onListBox(self, event):
        self.app_description.Clear()
        app = event.GetEventObject().GetStringSelection()
        print(app)
        status = os.popen(
            'cat "/home/pi/pi-apps/data/status/' + app + '"').read()
        status = status.rstrip('\n')
        if status == '':
            status = 'uninstalled'
        website = os.popen('cat "/home/pi/pi-apps/apps/' +
                           app + '/website"').read()
        website = website.rstrip('\n')

        description = os.popen('cat "/home/pi/pi-apps/apps/' +
                               app + '/description"').read()

        if website != '':
            self.app_description.AppendText("Status: " + status + "\n" +
                                "Website: " + website + "\n\n" + description)
        else:
            self.app_description.AppendText("Status: " + status + "\n\n" + description)

        self.app_description.WriteText(description)
        self.app_description.ShowPosition(0)



app = wx.App()
window(None, 'Pi-Apps').Center()
app.MainLoop()
