# -*- coding: utf-8 -*-

import wx
import wx.xrc
from formRunproc import FormRunproc
from formInsprogs import FormInsprogs

###########################################################################
## Class MainForm
###########################################################################

#----------------------------------------------------------------------
ID_exit = wx.NewIdRef()
ID_form_runproc = wx.NewIdRef()
ID_form_insprogs = wx.NewIdRef()
ID_about = wx.NewIdRef()
#----------------------------------------------------------------------

class FormMain(wx.MDIParentFrame):
    def __init__(self):
        wx.MDIParentFrame.__init__(self, None, -1, "My first program on Pyton", size=(800, 600))

        self.winCount = 0
        #self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        m__file = wx.Menu()
        #m__file.AppendSeparator()
        m__file.Append(ID_exit, "E&xit")

        m__tools = wx.Menu()
        m__tools.Append(ID_form_runproc, u"Running processes")

        m__tools.Append(ID_form_insprogs, u"Installed programs")

        m__help = wx.Menu()
        m__help.Append(ID_about, u"About")

        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_exit)
        self.Bind(wx.EVT_MENU, self.OnForm1, id=ID_form_runproc)
        self.Bind(wx.EVT_MENU, self.OnForm2, id=ID_form_insprogs)

        menubar = wx.MenuBar()
        menubar.Append(m__file, u"File")
        menubar.Append(m__tools, u"Tools")
        menubar.Append(m__help, u"Help")
        self.SetMenuBar(menubar)

        # self.m_statusBar1 = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)
        self.CreateStatusBar()

        self.Centre(wx.BOTH)

    def OnExit(self, evt):
        self.Close(True)

    def OnForm1(self, evt):
        self.winCount = self.winCount + 1
        win = FormRunproc(self, "Running processes")
        win.Show(True)

    def OnForm2(self, evt):
        self.winCount = self.winCount + 1
        win = FormInsprogs(self, "Installed programs")
        win.Show(True)

    def __del__(self):
        pass

#----------------------------------------------------------------------

class MyApp(wx.App):
    def OnInit(self):
        frame = FormMain()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(False)
app.MainLoop()
