#!/usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        gui_login.py
# Purpose:     Draw the log window, create epic list, Disclaimer
#
# Created:     26/05/2015
#-------------------------------------------------------------------------------


import sys
import wx
import wx.lib.agw.hyperlink as hl
import time
import personal
## Variables global
import globalvar

#-------------------------------------------------------------------------------
#
# Classe de la fenêtre "login"
#
#-------------------------------------------------------------------------------
class LogWindow(wx.Frame):

    def __init__(self, parent, title):
        """ Init Window """
        super(LogWindow, self).__init__(parent, title=title,size=(450, 520))
        self.InitUI()
        self.Centre()
        self.Show()


    def InitUI(self):
        """ Init Window Graphical Interface"""

        #Load Combobox with Epic dictionnary
        self.epic_choices = sorted(globalvar.epic_dict.keys()) #Tri AlphB de la list des keys

        # Create default value in "personal.py"
        self.createDefaultValues()

        # Create panel & sizer
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        ########################################################################
        # Icone de la fenêtre
        self.icon = wx.Icon('l3.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        # Logo L3 Scalping (coin haut droit)
        logo = wx.StaticBitmap(panel, bitmap=wx.Bitmap('L3.png'))
        sizer.Add(logo, pos=(0, 3), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)

        # Ligne de séparation
        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.BOTTOM, border=10)
        ########################################################################

        #Label username
        textUsername = wx.StaticText(panel, label="Username")
        sizer.Add(textUsername, pos=(2, 0), flag=wx.LEFT, border=5)
        # Textcontrol username
        self.tcUsername = wx.TextCtrl(panel,-1,personal.username)
        sizer.Add(self.tcUsername, pos=(2, 1), span=(1, 2), flag=wx.TOP|wx.EXPAND)

        #Label Password
        textPasswd= wx.StaticText(panel, label="Password")
        sizer.Add(textPasswd, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=5)
        #Textcontrol Password
        self.tcPasswd = wx.TextCtrl(panel,-1,personal.password.decode('base64'),style=wx.TE_PASSWORD)
        sizer.Add(self.tcPasswd, pos=(3, 1), span=(1, 2), flag=wx.TOP|wx.EXPAND, border=5)

        #Label API
        textApi = wx.StaticText(panel, label="API")
        sizer.Add(textApi, pos=(4, 0), flag=wx.LEFT|wx.TOP, border=5)
        #Textcontrol API
        self.tcApi = wx.TextCtrl(panel,-1,personal.api_key)
        sizer.Add(self.tcApi, pos=(4, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

        # CheckBox Demo
        self.chkDemo = wx.CheckBox(panel,-1,'Demo')
        self.chkDemo.SetValue(personal.is_demo)
        sizer.Add(self.chkDemo, pos=(5, 1), flag=wx.TOP|wx.LEFT, border=5)

        # Label Accounts
        textNbAccount = wx.StaticText(panel, label="Account [0,1,2]")
        sizer.Add(textNbAccount, pos=(6, 0), flag=wx.LEFT|wx.TOP, border=5)
        # Textcontrol Accounts
        self.tcNbAccount = wx.TextCtrl(panel,-1,personal.account_nb)
        sizer.Add(self.tcNbAccount, pos=(6, 1), span=(1, 1), flag=wx.TOP|wx.EXPAND, border=5)

        # Label Proxy
        textProxies = wx.StaticText(panel, label="Proxy (Optional)")
        sizer.Add(textProxies, pos=(7, 0), flag=wx.LEFT|wx.TOP, border=5)
        # textcontrol Proxy
        self.tcProxy = wx.TextCtrl(panel, -1, personal.proxies.get('https'))
        sizer.Add(self.tcProxy, pos=(7, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

        # Ligne de séparation
        line2 = wx.StaticLine(panel)
        sizer.Add(line2, pos=(8, 0), span=(1, 5), flag=wx.EXPAND|wx.TOP, border=10)
        ########################################################################

        # Label Epic
        textEpic = wx.StaticText(panel, label="Epic")
        sizer.Add(textEpic, pos=(9, 0), flag=wx.TOP|wx.LEFT, border=10)

        # Combo Epic
        self.combo = wx.ComboBox(panel,-1,choices=self.epic_choices)
        sizer.Add(self.combo, pos=(9, 1), span=(1, 3),flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=10)

        # Selection automatique de L'epic dans la liste si il existe dans personnal.py
        # sinon on definit le Dax par défaut
        if personal.epic !='':
            MonEpic = globalvar.epic_dict.keys()[globalvar.epic_dict.values().index(personal.epic)]
        else:
            MonEpic ='IX.D.DAX.IMF.IP'

        self.combo.SetStringSelection(MonEpic)

        # Ligne de séparation
        line3 = wx.StaticLine(panel)
        sizer.Add(line3, pos=(10, 0), span=(1, 5), flag=wx.EXPAND|wx.BOTTOM, border=5)
        ########################################################################

        # Disclaimer Panel
        boxDisclaimer = wx.StaticBox(panel, label="DISCLAIMER")
        boxDisclaimer.SetForegroundColour((255,0,0))
        boxsizer = wx.StaticBoxSizer(boxDisclaimer, wx.VERTICAL)

        # Disclaimer Checkbox
        self.chkCGU =wx.CheckBox(panel, label=u' Je certifie avoir lu, compris et accepté, les conditions générales\n d\'utilisation du logiciel \"L3 Scalping\"')
        self.chkCGU.SetForegroundColour((255,0,0))
        self.chkCGU.SetValue(False)

        # Add checkbox CGU to Disclaimer Panel
        boxsizer.Add(self.chkCGU,flag=wx.LEFT|wx.TOP, border=5)

        # Web links to L3 CGU on ANDLIL Website
        hyper1 = hl.HyperLinkCtrl(panel, -1, "Lire les C.G.U du logiciel L3 Scalping",URL="http://www.andlil.com/forum/scalping-l3-installation-mise-a-jour-explications-t8887.html")

        # Add weblink to Disclaimer Panel
        boxsizer.Add(hyper1,flag=wx.LEFT, border=25)

        # Bind to checkCGU function
        self.Bind(wx.EVT_CHECKBOX, self.checkCGU, self.chkCGU)

        # Add Panel Disclaimer to Sizer
        sizer.Add(boxsizer, pos=(11, 0), span=(1, 5),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM , border=10)
        ########################################################################

        # Boutton Exit, Bind on Self.close
        btnExit = wx.Button(panel, label="Exit")
        btnExit.Bind(wx.EVT_BUTTON, lambda _: self.Close())
        sizer.Add(btnExit, pos=(12, 2))

        #Button Connect
        self.btnConn = wx.Button(panel, label="Connect")
        # Set enable False by default
        self.btnConn.Enable(False)
        sizer.Add(self.btnConn, pos=(12, 3))


        sizer.AddGrowableCol(2)
        panel.SetSizer(sizer)

        ########################################################################

    def on_close(self):

        """ On window Close, Create a file "personnal.py" with configuration var
        """
        epic_key_selection = self.epic_choices[self.combo.GetCurrentSelection()]
        epic_value_selection = globalvar.epic_dict[epic_key_selection]

        config_vars = {"username": self.tcUsername.GetValue(),
                   "password": self.tcPasswd.GetValue(),
                   "is_demo": self.chkDemo.GetValue(),
                   "epic": epic_value_selection,
                   "api_key": self.tcApi.GetValue(),
                   "proxies": {"https": self.tcProxy.GetValue()},
                   "account_nb": self.tcNbAccount.GetValue()
                  }

        with open('personal.py', 'w') as config_file:
            for key, val in config_vars.iteritems():
                if key == 'password':
                    val = val.encode('base64')
                config_file.write("%s = %s\n" %(key, repr(val)))
                personal.__dict__[key] = val
        self.Close()



    def createDefaultValues (self):
        """ Create default values in "Personal.py" if this file is empty """

        self.default_values = {"username": '',
                  "password": '',
                  "is_demo": True,
                  "epic": 'IX.D.DAX.IMF.IP',
                  "api_key": '',
                  "proxies": {"https": '' },
                  "account_nb": '0'
              }
        for key in self.default_values:
            if not key in personal.__dict__:
                personal.__dict__[key] = self.default_values[key]


    def checkCGU(self,evt):

        """ Function to check / Uncheck the CGU Checkbox and
            Enable/Disable the connect button """

        self.btnConn.Enable(evt.IsChecked())

#-------------------------------------------------------------------------------
#
# Main
#
#-------------------------------------------------------------------------------
if __name__ == '__main__':

    app = wx.App()
    LogWindow(None, title="L3 Scalping GUI_LOGIN ONLY")
    app.MainLoop()

