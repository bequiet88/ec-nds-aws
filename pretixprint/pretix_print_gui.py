# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2019, webermann.net"
__license__ = "MIT"
__version__ = "0.1.0"
__email__ = "hauke@webermann.net"

import wx


class PretixBadgePrinter(wx.Frame):

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(PretixBadgePrinter, self).__init__(*args, **kw)

        self.lblname = wx.StaticText(self, label="Name :", pos=(20, 60))
        self.editname = wx.TextCtrl(self, value="", pos=(150, 60), size=(140, -1))
        self.Bind(wx.EVT_TEXT, self.EvtText, self.editname)

        self.insure = wx.CheckBox(self, label="Do you want Insured Shipment ?", pos=(20, 180))
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.insure)

        self.sampleList = ['Wochenende', 'Wochenende (Mitarbeiter)', 'Samstag', 'Samstag Abend', 'Sonntag']
        self.lblhear = wx.StaticText(self, label="Wähle das Ticket aus", pos=(20, 90))
        self.edithear = wx.ComboBox(self, pos=(150, 90), size=(150, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.edithear)
        self.Bind(wx.EVT_TEXT, self.EvtText, self.edithear)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready to Sync.")

        self.button = wx.Button(self, label="Print", pos=(50, 100))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                                    "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)

    def EvtComboBox(self, event):
        self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())

    def EvtText(self, event):
        self.logger.AppendText('EvtText: %s\n' % event.GetString())

    def EvtChar(self, event):
        self.logger.AppendText('EvtChar: %d\n' % event.GetKeyCode())
        event.Skip()

    def OnClick(self, event):
        self.logger.AppendText(" Click on object with Id %d\n" % event.GetId())

    def EvtCheckBox(self, event):
        self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())

if __name__ == '__main__':
    app = wx.App()
    frm = PretixBadgePrinter(None, title='Pretix Badge Printer')
    frm.Show()
    app.MainLoop()
