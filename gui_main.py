# -*- coding:utf-8 -*-

import sys
import wx
import time
import personal
import events #Import de events pour pouvoir appeler la fonction delete # Reflechir à la relocalisation de cette fonction et de cette evenement dans le main ...

## Variables global
import globalvar


LOGIN_SIZE = (800, 600)

def call_later(func):
   def func_wrapper(*args, **kwargs):
	  return wx.CallAfter(func, *args, **kwargs)
   return func_wrapper

def format(p) :
   p = float(p)
   #fonction a debuguyer plus tard
   #print("globalvar.scalingFactor",globalvar.scalingFactor, p)
   if globalvar.scalingFactor == 100: #Paire en XXX/JPY
	   p = p#return "3.3f"%(p)
   elif globalvar.scalingFactor == 10000: #Paire en XXX/USD OU XXX/EUR ou XXX/GBP
	   p = p#return "1.5f"%(p)
   elif globalvar.scalingFactor == 1: #Indice typiquement
	   p = p#return "5.1f"%(p)
   else:
	   p = p#return "%5.5f" %(p) #Format par défaut
   return "%d %3.2f" %(p/1000, p - int(p/1000)*1000)

class Window(wx.Frame):

   def __init__(self, parent, title, pivots, currencyCode, size):
	  super(Window, self).__init__(parent, title=title,
							 size = size)

      	  ##self.icon = wx.Icon('l3.ico', wx.BITMAP_TYPE_ICO)
          ##self.SetIcon(self.icon)
	  self.WIN_SIZE = size
	  self.init_ui(currencyCode)
	  self.Centre()
	  #Pivots#self.set_pivots(pivots)
	  self.Show()


   def init_ui(self, currencyCode):
	  self.statusbar = self.CreateStatusBar()

	  self.panel = wx.Panel(self, -1)
     
	  # Icone de la fenêtre
	  self.icon = wx.Icon('l3.ico', wx.BITMAP_TYPE_ICO)
	  self.SetIcon(self.icon)

      # Definition des widgets
	  button_size = wx.Size(40, 40)
	  text_size = wx.Size(50,25)      
	  self.buy_button = wx.Button(self.panel, -1, size=button_size)
	  self.buy_button.SetBackgroundColour((0,150,214)) #Fond Bleu ticket IG
	  self.buy_button.SetForegroundColour((255,255,255)) #Texte en blanc
	  self.buy_button.SetLabel('for LS')
	  self.sell_button = wx.Button(self.panel, -1, size=button_size)
	  self.sell_button.SetBackgroundColour((218,45,40)) #Fond en Rouge ticket IG
	  self.sell_button.SetForegroundColour((255,255,255)) #Texte en blanc
	  self.sell_button.SetLabel('Waiting')
	  self.spread_text = wx.StaticText(self.panel, -1, label="Spread : 01.0 - StopMin : 00.0 - StopMinGuaranted : 00.0", style=wx.CENTER)
	  self.is_Force_Open_text = wx.StaticText(self.panel, -1, label="Force Open", style=wx.TE_LEFT)
	  self.is_Force_Open_box = wx.CheckBox(self.panel, -1, style=wx.TE_RIGHT)
	  self.is_Force_Open_box.SetValue(globalvar.isForceOpen)
	  self.is_Keyboard_Trading_text = wx.StaticText(self.panel, -1, label="Keyboard Trading", style=wx.TE_LEFT)
	  self.is_Keyboard_Trading_box = wx.CheckBox(self.panel, -1, style=wx.TE_RIGHT)
	  self.is_Keyboard_Trading_box.SetValue(globalvar.isKeyBoardTrading)
	  self.is_Stop_Guaranteed_text = wx.StaticText(self.panel, -1, label="Guaranted Stop", style=wx.TE_LEFT)
	  self.is_Stop_Guaranteed_box = wx.CheckBox(self.panel, -1, style=wx.TE_RIGHT)
	  self.is_Stop_Guaranteed_box.SetValue(globalvar.isStopGuaranteed)
	  self.lot_size_text = wx.StaticText(self.panel, -1, label="Size", style=wx.TE_CENTRE)
	  self.lot_size = wx.TextCtrl(self.panel, -1, str(globalvar.requestDealSize), size=text_size, style=wx.TE_CENTER)
	  label_SL_Currency = "SL ("+str(currencyCode)+")"
	  self.SL_currency_text = wx.StaticText(self.panel, -1, label=label_SL_Currency, style=wx.TE_RIGHT)
	  self.SL_point_text = wx.StaticText(self.panel, -1, label="SL (point)", style=wx.TE_RIGHT)
	  self.SL_point = wx.TextCtrl(self.panel, -1, str(globalvar.SLpoint), size=text_size, style=wx.TE_CENTER)
	  self.TP_point_text = wx.StaticText(self.panel, -1, label="TP (point)", style=wx.TE_LEFT)
	  self.TP_point = wx.TextCtrl(self.panel, -1, str(globalvar.TPpoint), size=text_size, style=wx.TE_CENTER)
	  self.SL_currency = wx.TextCtrl(self.panel, -1, str(globalvar.SLcurrency), size=text_size, style=wx.TE_CENTER)
	  self.nb_pos = wx.StaticText(self.panel, -1, label="Amount of Position(s) : ")
	  self.taille_pos = wx.StaticText(self.panel, -1, label="Nb Sell = N/A - Nb Buy = N/A")
	  self.balance = wx.StaticText(self.panel, -1, label="Balance: N/A - Deposit: N/A")
	  self.pnl = wx.StaticText(self.panel, -1, label="PnL (EUR) : 0")
	  self.pnl_points = wx.StaticText(self.panel, -1, label="PnL (points) : 0")
	  # # #Pivots#self.pivots = [wx.StaticText(self.panel, -1, label=str(i)) for i in range(7)]
	  #Ajout Guilux PNL DAY
	  self.pnlDay = wx.StaticText(self.panel, -1, label="PNL Day: N/A")
	  self.closeAll_button = wx.Button(self.panel, -1, size=button_size)
	  self.closeAll_button.SetBackgroundColour((211,213,206))
	  self.closeAll_button.SetLabel('EMERGENCY CloseAll Tickets')
	  self.closeAllepic_button = wx.Button(self.panel, -1, size=button_size)
	  self.closeAllepic_button.SetBackgroundColour((211,213,206))
	  self.closeAllepic_button.SetLabel('CloseAll %s'%(globalvar.epic_to_shortname_dict.get(personal.epic)))
	  self.SLto0_button = wx.Button(self.panel, -1, size=button_size)
	  self.SLto0_button.SetBackgroundColour((211,213,206))
	  self.SLto0_button.SetLabel('SL to 0')
	  self.TPto0_button = wx.Button(self.panel, -1, size=button_size)
	  self.TPto0_button.SetBackgroundColour((211,213,206))
	  self.TPto0_button.SetLabel('TP to 0')
	  self.SLtoPRU_button = wx.Button(self.panel, -1, size=button_size)
	  self.SLtoPRU_button.SetBackgroundColour((211,213,206))
	  self.SLtoPRU_button.SetLabel('SL to PRU   N/A   ')

	  widgets = [self.sell_button, self.buy_button]
	  font1 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
	  for w in widgets:
		 w.SetFont(font1)

	  self.position_list = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT | wx.HSCROLL)
	  self.columns = [u'guaranteedStop', u'status', u'direction', u'limitLevel', u'level', u'affectedDeals', u'limitDistance', u'dealReference', u'dealStatus', u'dealId', u'reason', u'stopLevel', u'epic', u'stopDistance', u'expiry', u'size']
	  self.columns = [u'Status', u'Direction', u'Size', u'Open level', u'TP Level', u'SL Level', u'guaranteedStop', u'limitDistance', u'stopDistance', u'dealStatus', u'dealId', u'reason', u'epic', u'expiry', u'affectedDeals', u'dealReference'] #2015/04/17 Réordonnencement
	  map(lambda c: self.position_list.InsertColumn(*c), enumerate(self.columns))
	  for i in range(len(self.columns)):
		 self.position_list.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)

	  self.openpositions_list = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT)
	  self.columns = [u'trailingStopDistance', u'direction', u'openLevel',  u'size', u'dealID', u'currency', u'stopLevel', u'guarantedStop', u'trailingStep', u'creationDate', u'limitLevel', u'contractsize']
	  self.columns = [u'dealId', u'epic', u'size', u'direction',  u'Open Level', u'TP Level', u'SL level', u'Points']
	  map(lambda c: self.openpositions_list.InsertColumn(*c), enumerate(self.columns))
	  ####redimenssionement colonnes####
	  for i in range(len(self.columns)):
		 self.openpositions_list.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)


##########################################début modif beni_des_dieux (cf post forum)##########################################
	  ####utlisation d'un gridbagsizercome sizer principal####
	  main_box = wx.GridBagSizer(3, 3)
	  main_box.SetFlexibleDirection(wx.BOTH)
	  ####utlisation d'une boxsizer horizontal pour les bouttons buy/sell####
	  hbox_buy_sell = wx.BoxSizer(wx.HORIZONTAL)
	  hbox_buy_sell.Add(self.sell_button, wx.GROW |wx.EXPAND)
	  hbox_buy_sell.Add(self.buy_button, wx.GROW |wx.EXPAND)
	  main_box.Add(hbox_buy_sell, (0, 0), (1, 4), wx.EXPAND)
	  main_box.Add(self.spread_text, (1 ,0), (1, 4), wx.ALIGN_CENTRE)
	  main_box.Add(self.is_Keyboard_Trading_text, (2, 1), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
	  main_box.Add(self.is_Keyboard_Trading_box, (2, 2), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
	  main_box.Add(self.is_Force_Open_text, (3, 1), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
	  main_box.Add(self.is_Force_Open_box, (3, 2), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
	  main_box.Add(self.is_Stop_Guaranteed_text, (4, 1), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
	  main_box.Add(self.is_Stop_Guaranteed_box, (4, 2), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
	  main_box.Add(self.lot_size_text, (5, 1), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
	  main_box.Add(self.lot_size, (5, 2), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
	  main_box.Add(self.SL_point_text, (6, 1), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
	  main_box.Add(self.SL_point, (6, 2), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
	  main_box.Add(self.SL_currency_text, (7, 1), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
	  main_box.Add(self.SL_currency, (7, 2), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
	  main_box.Add(self.TP_point_text, (8, 1), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
	  main_box.Add(self.TP_point, (8, 2), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
	  ####utlisation d'une boxsizer horizontal pour les bouttons close all####
	  hbox_close_all = wx.BoxSizer(wx.HORIZONTAL)
	  hbox_close_all.Add(self.closeAll_button, wx.GROW |wx.EXPAND)
	  hbox_close_all.Add(self.closeAllepic_button, wx.GROW |wx.EXPAND)
	  main_box.Add(hbox_close_all, (9, 0), (1, 4), wx.EXPAND)
	  ####utlisation d'une boxsizer horizontal pour les bouttons sSL####
	  hbox_stop_to = wx.BoxSizer(wx.HORIZONTAL)
	  hbox_stop_to.Add(self.SLto0_button, wx.GROW |wx.EXPAND)
	  hbox_stop_to.Add(self.TPto0_button, wx.GROW |wx.EXPAND)
	  hbox_stop_to.Add(self.SLtoPRU_button, wx.GROW |wx.EXPAND)
	  main_box.Add(hbox_stop_to, (10, 0), (1, 4), wx.EXPAND)

	  main_box.Add(self.nb_pos, (11, 0), (1, 4),  wx.ALIGN_CENTRE)
	  main_box.Add(self.taille_pos, (12, 0), (1, 4),  wx.ALIGN_CENTRE)
	  main_box.Add(self.balance, (13, 0), (1, 4),  wx.ALIGN_CENTRE)
	  main_box.Add(self.pnl, (14, 0), (1, 4),  wx.ALIGN_CENTRE)
	  main_box.Add(self.pnl_points, (15, 0), (1, 4),  wx.ALIGN_CENTRE)
	  #Ajout Guilux Label Pnl Day
	  main_box.Add(self.pnlDay, (16, 0), (1, 4), wx.ALIGN_CENTRE)
	  main_box.Add(self.openpositions_list, (17, 0), (1, 4), wx.GROW | wx.EXPAND)
	  self.position_list.SetMinSize((self.WIN_SIZE[0]/4, 100))
	  main_box.Add(self.position_list, (18, 0), (1, 4), wx.GROW | wx.EXPAND)

	  for i in range(17):
	   main_box.AddGrowableRow(i)
	  for j in range(4):
	   main_box.AddGrowableCol(j)
##########################################fin modif beni_des_dieux##########################################

# ##########################################début modif beni_des_dieux (idée benoist)##########################################
#     ####utlisation d'un gridbagsizercome sizer principal####
#     main_box = wx.GridBagSizer(3, 3)
#     main_box.SetFlexibleDirection(wx.BOTH)
#     ####utlisation d'une boxsizer horizontal pour les bouttons buy/sell####
#     hbox_buy_sell = wx.BoxSizer(wx.HORIZONTAL)
#     hbox_buy_sell.Add(self.sell_button, wx.GROW |wx.EXPAND)
#     hbox_buy_sell.Add(self.buy_button, wx.GROW |wx.EXPAND)
#     main_box.Add(hbox_buy_sell, (0, 0), (1, 8), wx.EXPAND)

#     main_box.Add(self.spread_text, (1 ,1), (1, 1), wx.ALIGN_CENTRE)
#     main_box.Add(self.is_Keyboard_Trading_text, (1, 2), (1, 1), wx.ALIGN_CENTER)
#     main_box.Add(self.is_Keyboard_Trading_box, (1, 3), (1, 1), wx.ALIGN_CENTER)
#     main_box.Add(self.is_Force_Open_text, (1, 4), (1, 1), wx.ALIGN_CENTER)
#     main_box.Add(self.is_Force_Open_box, (1, 5), (1, 1), wx.ALIGN_CENTER)
#     main_box.Add(self.is_Stop_Guaranteed_text, (1, 6), (1, 1), wx.ALIGN_CENTER)
#     main_box.Add(self.is_Stop_Guaranteed_box, (1, 7), (1, 1), wx.ALIGN_CENTER)
#     main_box.Add(self.lot_size_text, (2, 0), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
#     main_box.Add(self.lot_size, (2, 1), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
#     main_box.Add(self.SL_point_text, (2, 2), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
#     main_box.Add(self.SL_point, (2, 3), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
#     main_box.Add(self.SL_currency_text, (2, 4), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
#     main_box.Add(self.SL_currency, (2, 5), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
#     main_box.Add(self.TP_point_text, (2, 6), (1, 1), wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
#     main_box.Add(self.TP_point, (2, 7), (1, 1), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
#     ####utlisation d'une boxsizer horizontal pour les bouttons close all####
#     hbox_close_all = wx.BoxSizer(wx.HORIZONTAL)
#     hbox_close_all.Add(self.closeAll_button, wx.GROW |wx.EXPAND)
#     hbox_close_all.Add(self.closeAllepic_button, wx.GROW |wx.EXPAND)
#     main_box.Add(hbox_close_all, (3, 0), (1, 8), wx.EXPAND)
#     ####utlisation d'une boxsizer horizontal pour les bouttons sSL####
#     hbox_stop_to = wx.BoxSizer(wx.HORIZONTAL)
#     hbox_stop_to.Add(self.SLto0_button, wx.GROW |wx.EXPAND)
#     hbox_stop_to.Add(self.SLto0spread_button, wx.GROW |wx.EXPAND)
#     hbox_stop_to.Add(self.SLtoPRU_button, wx.GROW |wx.EXPAND)
#     main_box.Add(hbox_stop_to, (4, 0), (1, 8), wx.EXPAND)

#     main_box.Add(self.nb_pos, (5, 0), (1, 8),  wx.ALIGN_CENTRE)
#     main_box.Add(self.taille_pos, (6, 0), (1, 8),  wx.ALIGN_CENTRE)
#     main_box.Add(self.balance, (7, 0), (1, 8),  wx.ALIGN_CENTRE)
#     main_box.Add(self.openpositions_list, (8, 0), (1, 8), wx.EXPAND)
#     self.position_list.SetMinSize((WIN_SIZE[0]/2, 200))
#     main_box.Add(self.position_list, (9, 0), (1, 8), wx.EXPAND)

#     for i in range(9):
#        main_box.AddGrowableRow(i)
#     for j in range(8):
#        main_box.AddGrowableCol(j)#
# ##########################################fin modif beni_des_dieux##########################################


##########################################old##########################################
	  # button_box = wx.BoxSizer(wx.HORIZONTAL)
	  # button_box.Add(self.sell_button, 1)
	  # button_box.Add(self.buy_button, 1)
	  # keyboardtrading_box = wx.BoxSizer(wx.HORIZONTAL)
	  # keyboardtrading_box.Add(self.is_Keyboard_Trading_box, 1, wx.ALIGN_RIGHT)
	  # keyboardtrading_box.Add(self.is_Keyboard_Trading_text, 1, wx.ALIGN_LEFT)
	  # ligne1_box = wx.BoxSizer(wx.HORIZONTAL)
	  # ligne1_box.Add(self.spread_text, 1,  wx.ALIGN_CENTER)
	  # ligne1_box.Add(keyboardtrading_box, 1,  wx.ALIGN_CENTER)
	  # requestsize_box = wx.BoxSizer(wx.HORIZONTAL)
	  # requestsize_box.Add(self.lot_size_text, 1, wx.ALIGN_RIGHT)
	  # requestsize_box.Add(self.lot_size, 1, wx.ALIGN_LEFT)
	  # forceopen_box = wx.BoxSizer(wx.HORIZONTAL)
	  # forceopen_box.Add(self.is_Force_Open_box, 1, wx.ALIGN_CENTER)
	  # forceopen_box.Add(self.is_Force_Open_text, 1, wx.ALIGN_CENTER)
	  # ligne2_box = wx.BoxSizer(wx.HORIZONTAL)
	  # ligne2_box.Add(requestsize_box, 1,  wx.ALIGN_CENTER)
	  # ligne2_box.Add(forceopen_box, 1, wx.ALIGN_CENTER)
	  # SL_point_box = wx.BoxSizer(wx.HORIZONTAL)
	  # SL_point_box.Add(self.SL_point_text, 1, wx.ALIGN_RIGHT)
	  # SL_point_box.Add(self.SL_point, 1, wx.ALIGN_LEFT)
	  # TP_box = wx.BoxSizer(wx.HORIZONTAL)
	  # TP_box.Add(self.TP_point, 1, wx.ALIGN_RIGHT)
	  # TP_box.Add(self.TP_point_text, 1, wx.ALIGN_LEFT)
	  # ligne3_box = wx.BoxSizer(wx.HORIZONTAL)
	  # ligne3_box.Add(SL_point_box, 1, wx.ALIGN_CENTER)
	  # ligne3_box.Add(TP_box, 1, wx.ALIGN_CENTER)
	  # SL_currency_box = wx.BoxSizer(wx.HORIZONTAL)
	  # SL_currency_box.Add(self.SL_currency_text, 1, wx.ALIGN_RIGHT)
	  # SL_currency_box.Add(self.SL_currency, 1, wx.ALIGN_LEFT)
	  # ligne4_box = wx.BoxSizer(wx.HORIZONTAL)
	  # ligne4_box.Add(SL_currency_box, 1, wx.ALIGN_CENTER)
	  # ligne4_box.Add(wx.StaticText(self.panel, -1, label=" !!! SLcurrency field not send to IG !!! If SL point is not blank then Size is evaluate "), 1, wx.ALIGN_CENTER)
	  # stopguaranteed_box = wx.BoxSizer(wx.HORIZONTAL)
	  # stopguaranteed_box.Add(self.is_Stop_Guaranteed_box, 1, wx.ALIGN_CENTRE)
	  # stopguaranteed_box.Add(self.is_Stop_Guaranteed_text, 1, wx.ALIGN_CENTRE)
	  # closeall_box = wx.BoxSizer(wx.HORIZONTAL)
	  # closeall_box.Add(self.closeAll_button, 1, wx.ALIGN_CENTER)
	  # closeall_box.Add(self.closeAllepic_button, 1, wx.ALIGN_CENTER)
	  # ligne5_box = wx.BoxSizer(wx.HORIZONTAL)
	  # ligne5_box.Add(closeall_box, 1, wx.ALIGN_CENTER)
	  # ligne5_box.Add(stopguaranteed_box, 1, wx.ALIGN_CENTER)
	  # ligne6_box = wx.BoxSizer(wx.HORIZONTAL)
	  # ligne6_box.Add(self.SLto0_button, 1, wx.ALIGN_CENTER)
	  # ligne6_box.Add(self.SLto0spread_button, 1, wx.ALIGN_CENTER)
	  # ligne6_box.Add(self.SLtoPRU_button, 1, wx.ALIGN_CENTER)
	  # box = wx.BoxSizer(wx.VERTICAL)
	  # box.Add(button_box, 1, wx.EXPAND | wx.ALL, 10 )
	  # box.Add(ligne1_box, 1, wx.ALIGN_CENTER)
	  # box.Add(ligne2_box, 1, wx.ALIGN_CENTER)
	  # box.Add(ligne3_box, 1, wx.ALIGN_CENTER)
	  # box.Add(ligne4_box, 1, wx.ALIGN_CENTER)
	  # box.Add(ligne5_box, 1, wx.ALIGN_CENTER)
	  # box.Add(ligne6_box, 1, wx.ALIGN_CENTER)
	  # box.Add(self.nb_pos, 1, wx.ALIGN_CENTER)
	  # box.Add(self.taille_pos, 1, wx.ALIGN_CENTER)
	  # box.Add(self.balance, 1, wx.ALIGN_CENTER)
	  #Pivots#for p in self.pivots:
	  #Pivots#    box.Add(p, 1, wx.ALIGN_CENTER)
	  # box.Add(self.openpositions_list, 1, wx.EXPAND)
	  # box.Add(self.position_list, 1, wx.EXPAND)
##########################################fin old##########################################


	   main_box.SetSizeHints(self.panel)
	   self.panel.SetSizerAndFit(main_box)
	   self.update_balance()
	   # self.update_price(11000.62, 11000.12)

	   self.total_pnl = 0
	   self.history = {}

   @call_later
   def update_forceOpen(self, item):

	  globalvar.isForceOpen = self.is_Force_Open_box.GetValue()
	  if globalvar.isForceOpen == False:
		 globalvar.SLpoint = ''
		 globalvar.TPpoint = ''
		 globalvar.SLcurrency = ''
		 self.SL_point.SetValue(str(globalvar.SLpoint))
		 self.TP_point.SetValue(str(globalvar.TPpoint))
		 self.SL_currency.SetValue(str(globalvar.SLcurrency))
	  #print("--- Fonction update_foreceopen : globalvar.isForceOpen/SLpoint/TPpoint/SLcurrency", globalvar.isForceOpen, globalvar.SLpoint, globalvar.TPpoint, globalvar.SLcurrency) #Ok

   def update_keyboardtrading(self, item):
	  globalvar.isKeyBoardTrading = self.is_Keyboard_Trading_box.GetValue()
	  #print("--- Fonction update_keyboardtrading : ", globalvar.isKeyBoardTrading) # Ok

   def update_stopGuaranteed(self, item):
	  print(" Fonction update_stopGuaranteed ", self.SL_point.GetValue())
	  if self.SL_point.GetValue() != u'':
		 try:
			value = float(self.SL_point.GetValue())
		 except ValueError:
			value = 0
		 if value > 0 :
			globalvar.isStopGuaranteed = self.is_Stop_Guaranteed_box.GetValue()
	  else:
		 globalvar.isStopGuaranteed = False
		 self.is_Stop_Guaranteed_box.SetValue(globalvar.isStopGuaranteed)
	  #print("mise a jour Variable Stop Varantie", globalvar.isStopGuaranteed) # Ok

   @call_later
   def update_sizelot(self, item):

	  value = self.lot_size.GetValue().replace(",",".")
	  if value != '':
		 try:
			globalvar.requestDealSize = round(float(value),2) #Arrondi mathematique de la valeur rentrée à deux decimal avec la fonction format
		 except ValueError:
			globalvar.requestDealSize = ''
			self.lot_size.SetValue(globalvar.requestDealSize)
	  else:
		 globalvar.requestDealSize = value
	  #print("Fonction update_sizelot : ", globalvar.requestDealSize) #Ok

   @call_later
   def update_SLpoint(self, item):
	  value = self.SL_point.GetValue().replace(",",".")
	  if value != '':
		 try:
			globalvar.SLpoint = round(float(value),1) #Arrondi mathematique de la valeur rentrée à une decimale avec la fonction format
			#MaJ du Force Open
			globalvar.isForceOpen = True
			self.is_Force_Open_box.SetValue(globalvar.isForceOpen)
		 except ValueError:
			globalvar.SLpoint = ''
			self.SL_point.SetValue(globalvar.SLpoint)
			print("SLpoint Error")

		 if globalvar.SLcurrency != '':
			#calcul du nombre de position avec la formule : (SLcurrency)/(SLpoint + spread)/valpoint = nb de lots
			try:
			   globalvar.requestDealSize = round(globalvar.SLcurrency / (globalvar.SLpoint + globalvar.spread) / globalvar.valueOfOnePip ,2)
			   self.lot_size.SetValue(str(globalvar.requestDealSize)) #MàJ du champ dans la taille du lot
			except ValueError:
			   globalvar.requestDealSize = ''
			   print("SLpoint -> SLcurrency : Error")
	  else:
		 globalvar.SLpoint = value

		 #Mise à False  isStopGuaranteed si SL est vide
		 globalvar.isStopGuaranteed = False
		 self.is_Stop_Guaranteed_box.SetValue(globalvar.isStopGuaranteed)

		 #Mise à False isForceOpen si TP & SL sont vide
		 if globalvar.TPpoint == '':
			globalvar.isForceOpen = False
			self.is_Force_Open_box.SetValue(globalvar.isForceOpen)


	  #print("--- Fonction globalvar.SLpoint : globalvar.SLpoint/TPpoint/SLcurrency", globalvar.SLpoint,globalvar.TPpoint, globalvar.SLcurrency) #Ok

   @call_later
   def update_TPpoint(self, item):
	  value = self.TP_point.GetValue().replace(",",".")
	  if value != '':
		 try:
			globalvar.TPpoint = round(float(value),1) #Arrondi mathematique de la valeur rentrée à une decimale avec la fonction format
			globalvar.isForceOpen = True
			self.is_Force_Open_box.SetValue(globalvar.isForceOpen)
		 except ValueError:
			globalvar.TPpoint = ''
			self.TP_point.SetValue(globalvar.TPpoint)
			print("TPpoint Error")
	  else:
		 globalvar.TPpoint = value
		 if globalvar.SLpoint == '':
			globalvar.isForceOpen = False
			self.is_Force_Open_box.SetValue(globalvar.isForceOpen)
	  #print("Fonction globalvar.TPpoint : ", globalvar.TPpoint) #Ok


   @call_later
   def update_SLcurrency(self, item):
	  value = self.SL_currency.GetValue().replace(",",".")
	  if value != '':
		 try:
			globalvar.SLcurrency = round(float(value),2) #Arrondi mathematique de la valeur rentrée à deux decimales avec la fonction format
			if globalvar.SLpoint != '':
			   #calcul du nombre de position avec la formule : (SLcurrency)/(SLpoint + globalvar.spread)/valpoint = nb de lots
			   globalvar.requestDealSize = round(globalvar.SLcurrency / (globalvar.SLpoint + globalvar.spread) / globalvar.valueOfOnePip ,2)
			   self.lot_size.SetValue(str(globalvar.requestDealSize)) #MaJ du champ dans la GUI
		 except ValueError:
			globalvar.SLcurrency = ''
			self.SL_currency.SetValue(globalvar.SLcurrency)
	  else:
		 #Si le SL est remis à zéro alors, le nombre de lot est également remis à zéro
		 globalvar.SLcurrency = value
		 globalvar.requestDealSize = ''
		 self.lot_size.SetValue(str(globalvar.requestDealSize)) #MaJ du champ dans la GUI
	  #print("--- Fonction update_SLcurrency : ", globalvar.SLcurrency, globalvar.requestDealSize)

   @call_later
   def update_price(self, bid, ask, sum_point):
	#print("--- update_price ---")   
	#MàJ du prix du spread, bid, ask, pnl par ligne active + total et timestamp
	self.buy_button.SetLabel(bid)
	self.sell_button.SetLabel(ask)
	self.statusbar.SetStatusText("last updated: " + time.strftime("%H:%M:%S"))
	globalvar.spread = round(float((float(bid)-float(ask)) * globalvar.scalingFactor),1)
	self.spread_text.SetLabel("Spread : %s - StopMin : %s - StopMinGuaranted : %s" %(globalvar.spread,globalvar.minNormalStoporLimitDistance, globalvar.minControlledRiskStopDistance))

	####màj de la liste des pos####
	for item, dealId in enumerate(globalvar.dict_openposition):
		#print("item, dealId", item, dealId) 
		try:
			point_profit = globalvar.dict_openposition.get(dealId).get('pnl')
			#Ajout/MàJ du solde en point par ligne dans le tableau
			self.openpositions_list.SetStringItem(item, 7, str(point_profit))
			#avec le bonne couleur
			if point_profit < 0:
				self.openpositions_list.SetItemTextColour(item, (218, 45, 40))
			elif point_profit > 0:
				self.openpositions_list.SetItemTextColour(item, (0, 150, 214))
			elif point_profit == 0:
				self.openpositions_list.SetItemTextColour(item, (0, 150, 14))
			if str(point_profit) == 'N/A':
				self.openpositions_list.SetItemTextColour(item, (0, 0, 0))
		except KeyError:
			pass

	#Ajout/MàJ du solde en point dans le tableau avec le bonne couleur
	self.pnl_points.SetLabel('PnL (points) : ' + str(sum_point))
	if sum_point < 0 :
		self.pnl_points.SetForegroundColour((218, 45, 40))
	elif sum_point == 0.00:
		self.pnl_points.SetForegroundColour((0 ,150, 14))
	elif sum_point > 0:
		self.pnl_points.SetForegroundColour((0, 150, 214))

	  #print ("---fonction update_price--- spread", globalvar.spread)


   @call_later
   def update_balance(self, balance='N/A', pnl='0', deposit='N/A'):
	  #self.nb_pos.SetLabel( "Nb pos: %s" %  nb_pos)
	  self.balance.SetLabel( "balance: %s, deposit: %s" % (balance, deposit))
	  ###màj label en fonction du pnl####
	  self.pnl.SetLabel('PnL (EUR) : ' + pnl)
	  try:
		 if float(pnl) < 0 :
			self.pnl.SetForegroundColour((218,45,40))
		 elif float(pnl) == 0.00:
			self.pnl.SetForegroundColour((0,150,14))
		 elif float(pnl) > 0:
			self.pnl.SetForegroundColour((0,150,214))

	  except ValueError:
		 print("Erreur dans gui.update_balance, Value Error", pnl)
		 #self.pnl.SetLabel('PNL (EUR) : ' + pnl)
		 #self.pnl.SetForegroundColour((0,150,14))


   @call_later
   def update_pos(self, nb_ticket='NA', sizeBuy='NA', sizeSell='NA'):
	  self.nb_pos.SetLabel( "Nb pos: %s" %  nb_ticket)
	  #Creation de cette fonction pour mettre a jour uniquement nb_ticket, sizeSell et sizeBuy
	  self.taille_pos.SetLabel( "Sell = %s - Buy = %s" %  (sizeSell, sizeBuy))

   @call_later
   def add_OPUmessage(self, pos):
	  index = self.position_list.InsertStringItem(0, '')#Ajoute une ligne en haut de la liste
	  for i, p in enumerate(pos):
		 self.position_list.SetStringItem(index, i, str(p))

   @call_later
   def set_openpositions(self, pos):
      #pos = open_position
	  #print("--- Fonction gui_main.set_openpositions ---")
	  #Reçoit {"dealdId":{epic:'', size:'', direction:'', openLevel:'', TP:'', SL:'', pnl:''} , ...}

	  #Efface les items de la liste
      self.openpositions_list.DeleteAllItems()

	  #Met les valeurs dans la liste
      for dealId in pos:
         index = self.openpositions_list.InsertStringItem(65000, '')#Ajoute 1 ligne en bas -> utilisation d'un subterfuge avec ligne à 65000)
         i = 0
         self.openpositions_list.SetStringItem(index, i, str(dealId)) #Ajoute le dealId dans la première colonne
         ### Modification pour utilisation dico v2, parcours du sous-dico avec une liste ordonné sinon le dico est enregistré dans n'importe quel ordre
         dict_value = pos.get(dealId)
         for key in globalvar.list_key:
            c = dict_value.get(key)
            i = i + 1
            if globalvar.epic_to_shortname_dict.get(c) <> None:
                c = globalvar.epic_to_shortname_dict.get(c) #Chagne l'epic par un nomc ourt
            self.openpositions_list.SetStringItem(index, i, str(c)) #Met les valeurs dans chaque colonne
	  #print("--- fin ---")

   @call_later
   def set_pivots(self, pivots):
	  labels = "R3 R2 R1 P S1 S2 S3".split()
	  for i, p in enumerate(pivots[::-1]):
		 p = format(p)
		 self.pivots[i].SetLabel(labels[i] + ": " + p)
		 color = (255, 0, 0) if i > 3 else (0, 255, 0) if i < 3  else (0, 0, 0)
		 self.pivots[i].SetForegroundColour(color)

   @call_later
   def OnClick_openpositionslist(self, event):
	  #print("--- fonction OnClick_openpositionslist ---")
	  dealId_todelete = str(self.openpositions_list.GetItemText(self.openpositions_list.GetFirstSelected()))

	  direction = globalvar.dict_openposition.get(dealId_todelete).get('direction')
	  size = globalvar.dict_openposition.get(dealId_todelete).get('size')
	  #print ("DealId a supprimer ", dealId_todelete, direction , size)
	  events.delete(dealId_todelete, direction, size) #Appel du events-> delete
	  #print ("--- FIN  gui.OnClick_openpositionslist ---")

   @call_later
   def update_pru(self, pru='NA'):
	  #self.nb_pos.SetLabel( "Nb pos: %s" %  nb_pos)
	  #Ajout Deposit
	  self.SLtoPRU_button.SetLabel( "SL to PRU %s" % (pru))

   #Ajout Guilux: permet d'afficher dans le label le PNL Journalier
   @call_later
   def update_pnlDaily(self, pnlEuro='0', pnlPoints='0',nbTrades='0'):
		chaineFormatee = str(pnlPoints)+' point(s) | ' + str(pnlEuro )+ ' E | '+str(nbTrades)+' Trade(s)'
		self.pnlDay.SetLabel("PNL Day : %s" %(chaineFormatee))
		try:
             		float(pnlPoints)
            		if float(pnlPoints) < 0 :
                		self.pnlDay.SetForegroundColour((218,45,40))
             		elif float(pnlPoints) == 0.00:
                		self.pnlDay.SetForegroundColour((0,150,14))
             		elif float(pnlPoints) > 0:
                		self.pnlDay.SetForegroundColour((0,150,214))

        	except ValueError:
             		self.pnlDay.SetForegroundColour((0,150,14))


if __name__ == "__main__":
   app = wx.App()
   #window = LogWindow(None)

   #Def variables pour le lancement de l'interface GUI seule
   globalvar.valueOfOnePip = 5 #Valeur en monnaie d'un pip
   globalvar.scalingFactor = 1.0 #Valeur du facteur d'échelle
   globalvar.spread = 1.0  #Valeur du spread
   globalvar.dict_openposition = { "DDDAAAZZZ" : {'epic':"miniDAX30(5E)", 'size': "10.5", 'direction': "Buy", 'open_level':"11997.4", "limit_level": None, "stop_level": None, "pnl":'N/A'}, "BBBCCCYYY" : {'epic':"miniDAX30(5E)",'size':  "2.5", 'direction': "Sell", 'open_level':"12055.3",  "limit_level": None, "stop_level": None, "pnl":'N/A'}} # Dictionnaire avec des positions fictives

   #lancement de l'interface et binding des différents functions
   width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
   height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
   WIN_SIZE = (width/4, height/1.2)
   window = Window(None, pivots=[100,200,300,400,500,600,700], title='L3 scalping - GUIONLY', currencyCode = "EUR", size = (WIN_SIZE))
   window.lot_size.Bind(wx.EVT_TEXT, window.update_sizelot)
   window.SL_point.Bind(wx.EVT_TEXT, window.update_SLpoint)
   window.TP_point.Bind(wx.EVT_TEXT, window.update_TPpoint)
   window.SL_currency.Bind(wx.EVT_TEXT, window.update_SLcurrency)
   window.is_Force_Open_box.Bind(wx.EVT_CHECKBOX, window.update_forceOpen)
   window.is_Keyboard_Trading_box.Bind(wx.EVT_CHECKBOX, window.update_keyboardtrading)
   window.openpositions_list.Bind(wx.EVT_LIST_ITEM_SELECTED, window.OnClick_openpositionslist)
   window.is_Stop_Guaranteed_box.Bind(wx.EVT_CHECKBOX, window.update_stopGuaranteed)

   # Remplissage de la liste des positions ouvertes
   window.set_openpositions(globalvar.dict_openposition)

   app.MainLoop()

