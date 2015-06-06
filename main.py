# -*- coding:utf-8 -*-

### Version 1.16 falex du 2015 06 01
### Sur base 1.15.1 falex/guilux/beni du 2015 06 01

### Ajouts fonctionnels / modifications / corrections :
### - Ajout d'un polling toutes les 60 de la valeur des Stops (Normal et Garantie) à l'ouverture 

# L3 Scalping
# Import Librairies système
import os
import glob
import time
import logging
import wx
import requests
import json
import threading
import random

# Import modules programme
import igls
import gui_main, gui_login
import urls
import events
import personal

## Variables global
import globalvar

##

###definition de la variable d'environnement pour les certificats SSL (a faire pour l'application, à ne pas mettre pour l'utilisation direct dans python)####
# os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), 'cacert.pem')


def buy(event): order(event, "BUY", globalvar.requestDealSize, globalvar.isForceOpen, globalvar.SLpoint, globalvar.TPpoint, globalvar.isStopGuaranteed)
def sell(event): order(event, "SELL", globalvar.requestDealSize, globalvar.isForceOpen, globalvar.SLpoint, globalvar.TPpoint, globalvar.isStopGuaranteed)

def order(event, direction, reqDealSize, isForceOpen, SLpoint, TPpoint, isStopGuaranteed):
    expiry = '-'
    if reqDealSize < globalvar.minDealSize:
        globalvar.dealSizeDelta = globalvar.minDealSize - reqDealSize
        reqDealSize = globalvar.minDealSize
    else:
        globalvar.dealSizeDelta = 0
    body = {"currencyCode": globalvar.currencyCode, "epic": personal.epic, "expiry": expiry, "direction": direction, "size": reqDealSize, "forceOpen": isForceOpen, "guaranteedStop": False, "orderType": "MARKET", "limitDistance": TPpoint, "stopDistance": SLpoint, "guaranteedStop": isStopGuaranteed}
    r = requests.post(urls.neworderurl, data=json.dumps(body), headers=urls.fullheaders, proxies=personal.proxies)
    if r.status_code == 200:
        dealReference = r.json().get(u'dealReference')
        print("-- Fonction order ---\n   Ok Code %s"%(r.status_code))
        ###Debug dans la console, je met en commentaire car le message d'erreur du trade apparait dans la sous-fenêtre OPU###
        ###print("-- Fonction order --- Order Ok\n    Code %s\n    Reponse %s"%(r.status_code, r.content))
        ###r = requests.get(urls.confirmsurl%(dealReference), headers=urls.fullheaders, proxies=personal.proxies)
    	###if r.status_code == 200:
        ###    s = json.loads(r.content)
        ###    #print("-- Fonction order --- Confirms Ok\n    Code %s\n    URL %s\n    Reponse %s"%(r.status_code,urls.confirmsurl%(dealReference), r.content))
        ###    print("-- Fonction order --- Confirms Ok\n    Code %s\n    URL %s\n    Status %s\n    Reason %s\n    dealStatus %s"%(r.status_code,urls.confirmsurl%(dealReference), s.get(u'status'), s.get(u'reason'), s.get(u'dealStatus')))
        ###else:
        ###    print("--- Fonction order --- Confirms Erreur\n    Erreur Code %s\n    URL %s\n    Reponse %s"%(r.status_code,urls.confirmsurl%(dealReference), r.content))
    else:
        print("--- Fonction order ---\n    Erreur Code %s\n    Body %s\n    Reponse %s"%(r.status_code,body, r.content))

def calculatePivots():
    r = requests.get(urls.pricesurl % (personal.epic, 'DAY'), headers=urls.fullheaders, proxies=personal.proxies)
    s = json.loads(r.content).get('prices')[0]

    H = (s.get('highPrice').get('ask')  + s.get('highPrice').get('bid')) / 2
    B = (s.get('lowPrice').get('ask')  + s.get('lowPrice').get('bid')) / 2
    C = (s.get('closePrice').get('ask')  + s.get('closePrice').get('bid')) / 2

    Pivot = (H + B + C) / 3
    S1 = (2 * Pivot) - H
    S2 = Pivot - (H - B)
    S3 = B - 2* (H - Pivot)
    R1 = (2 * Pivot) - B
    R2 = Pivot + (H - B)
    R3 = H + 2* (Pivot - B)

    return S3, S2, S1, Pivot, R1, R2, R3

def pollingMarketsDetails(period=60):
    #Lance la comman de getmarketDetail dans un thread toute les 'period' secondes pour mettre à jour les variables de deadling du contrat.
    while True:
        globalvar.minDealSize, globalvar.currencyCode, globalvar.valueOfOnePip, globalvar.scalingFactor, globalvar.minNormalStoporLimitDistance, globalvar.minControlledRiskStopDistance = getMarketsDetails()
        #DEBUG START#
        #globalvar.minNormalStoporLimitDistance += random.randint(1,10)
        #print("pollingMarketsDetails %ssecondes %s - minStopNormal=%s - minStopG=%s"%(period, datetime.datetime.now(),globalvar.minNormalStoporLimitDistance, globalvar.minControlledRiskStopDistance))
        #DEBUG END#
        time.sleep(period)
    
#Ajout falex pour récuperation du minDealSize de l'epic choisi
def getMarketsDetails():
    #print("getMarketDetails URL %s---"%urls.marketsurl % (personal.epic))
    #print("getMarketDetails header %s---"%urls.fullheaders)
    #Utilisation du header Version:2 car bug avec Version:1 -> Error 500 {error system}, j'ai envoyé un message sur labs.ig.com le 31/05/2015
    r = requests.get(urls.marketsurl % (personal.epic), headers=urls.fullheaders_v2, proxies=personal.proxies)
    #print("getMarketDetails r.content %s"%r.content)
    j = json.loads(r.content)

    i = j.get(u'instrument') #Sous-partie instrument
    valueOfOnePip = float(i.get(u'valueOfOnePip'))
    ic = i.get(u'currencies')  
    #currencies_code = ic[0].get(u'name') #Ajout 2015 03 09 pour recuperer la monnnais d'échange du sous-jacent
    currencies_code = ic[0].get(u'code') #Correction en version2 'name' devient 'code' la monnnais d'échange du sous-jacent
    
    dR = j.get(u'dealingRules') #Sous-partie dealingRules
    #print(dR)
    minDealSize = 0
    dm = dR.get(u'minDealSize')
    if dm.get(u'unit') == u'POINTS':
         minDealSize = dm.get(u'value')
    
    minNormalStoporLimitDistance = None
    nsd = dR.get(u'minNormalStopOrLimitDistance')
    #print(nsd)
    if nsd.get(u'unit') == u'POINTS':
         minNormalStoporLimitDistance = nsd.get(u'value')
         #print("minNormalStoporLimitDistance %s"%(minNormalStoporLimitDistance))
         
    minControlledRiskStopDistance = None
    csd = dR.get(u'minControlledRiskStopDistance')
    #print(csd)
    if nsd.get(u'unit') == u'POINTS':
         minControlledRiskStopDistance = csd.get(u'value')
         #print("minControlledRiskStopDistance %s"%(minControlledRiskStopDistance))
         
    s = j.get(u'snapshot') #Sous-partie snapshot
    scalingFactor = float(s.get(u'scalingFactor'))
    #print("--- Fonction getMarketsDetails ---  ", minDealSize, currencies_code, valueOfOnePip, scalingFactor)
    return minDealSize, currencies_code, valueOfOnePip, scalingFactor, minNormalStoporLimitDistance, minControlledRiskStopDistance #renvoi une valeur en point et la monnaie d'execution, la valeur d'un pip

def getDailyPrices():
    url = 'https://' + urls.ig_host + '/gateway/deal/prices/%s/%s/%d' %  (personal.epic, 'MINUTE', 100000)
    r = requests.get(url, headers=urls.fullheaders, proxies=personal.proxies)
    s = json.loads(r.content)
    import pickle
    with open('Logs/quotesobjectv2.pickle', 'w') as f: pickle.dump(s,  f)

def OnKeyPress(event):
    #print(" Fonction Main OnKeyPress ")
    code = event.GetKeyCode()
    if (globalvar.isKeyBoardTrading) :
        #if code == wx.WXK_UP:
            #print("Up")
            #events.get_openPositions()
        if code == wx.WXK_CONTROL:
            print("Ctrl/Cmd")
            last_pos_id = globalvar.dict_openposition.keys()[-1]
            direction = globalvar.dict_openposition.get(last_pos_id).get('direction')
            size = globalvar.dict_openposition.get(last_pos_id).get('size')
            events.delete(last_pos_id, direction, size) #Appel du events-> delete
        if code == wx.WXK_LEFT:
            print("Left")
            order(event, "SELL", globalvar.requestDealSize, globalvar.isForceOpen, globalvar.SLpoint, globalvar.TPpoint, globalvar.isStopGuaranteed)
        if code == wx.WXK_RIGHT:
            print("Right")
            order(event, "BUY", globalvar.requestDealSize, globalvar.isForceOpen, globalvar.SLpoint, globalvar.TPpoint, globalvar.isStopGuaranteed)
        if code == wx.WXK_DOWN:
            print("Down")
            CloseAll() #Appel de la fonction pour fermer tous les ordres ouverts avec une copie du dictionnaire
        """
        if code == wx.WXK_ESCAPE:
            print("Escape")
        if code == wx.WXK_RETURN:
            print("Return")
        """
    event.Skip()
    #print(" Fin ")

def CloseAllButton(event): CloseAll()

def CloseAll():
    #print ("--- Fonction CloseAll ---")
    for dealId_todelete, v in globalvar.dict_openposition.items():
        direction = v.get('direction')
        size = v.get('size')
        events.delete(dealId_todelete, direction, size) #Appel du events-> delete
    #print(" Fin ")

def CloseAllepicButton(event):
    #print ("--- Fonction Close All epic ---")
    for dealId_todelete, v in globalvar.dict_openposition.items():
        if v.get('epic') == personal.epic:
            direction = v.get('direction')
            size = v.get('size')
            events.delete(dealId_todelete, direction, size) #Appel du events-> delete
    #print("--- Fin Close All epic ---")
    
def SLto0(event):
    #print("SL to 0 ", personal.epic)
    for dealId in globalvar.dict_openposition:
        if globalvar.dict_openposition.get(dealId).get('epic') == personal.epic:
            o = float(globalvar.dict_openposition.get(dealId).get('open_level'))
            tp = globalvar.dict_openposition.get(dealId).get('limit_level')
            events.updateLimit(dealId, o, tp)

def SLto0spread(event):
    #print("SL to 0 - spread ",personal.epic)
    for dealId in globalvar.dict_openposition:
        if globalvar.dict_openposition.get(dealId).get('epic') == personal.epic:
            o = float(globalvar.dict_openposition.get(dealId).get('open_level'))
            o = o - (globalvar.spread/globalvar.scalingFactor)
            tp = globalvar.dict_openposition.get(dealId).get('limit_level')
            events.updateLimit(dealId, o, tp)

def TPto0(event):
    #print("TP to 0 - ",personal.epic)
    #print("globalvar.dict_openposition", globalvar.dict_openposition)
    for dealId in globalvar.dict_openposition:
        if globalvar.dict_openposition.get(dealId).get('epic') == personal.epic:
            o = float(globalvar.dict_openposition.get(dealId).get('open_level'))
            sl = globalvar.dict_openposition.get(dealId).get('stop_level')
            events.updateLimit(dealId, sl, o)

def SLtoPRU(event):
    #print("SL to PRU ",personal.epic)
    pru = events.PRU(personal.epic)
    #print("PRU = %s" %pru)
    for dealId in globalvar.dict_openposition:
        if globalvar.dict_openposition.get(dealId).get('epic') == personal.epic:
            tp = globalvar.dict_openposition.get(dealId).get('limit_level')
            events.updateLimit(dealId, pru, tp)



##############################################################################
def main(event):
    loging_window.on_close()

    # Connecting to IG
    urls.set_urls()
    print("Connecting as %s"%personal.username)
    logger_debug.info("Connecting as %s"%personal.username)
    r = requests.post(urls.sessionurl, data=json.dumps(urls.payload), headers=urls.headers, proxies=personal.proxies)
    if r.status_code != 200:
        print("--- Login Error ---\n    Erreur Code %s, Reponse %s"%(r.status_code, r.content))
        logger_debug.error("--- Login Error ---\n    Erreur Code %s, Reponse %s"%(r.status_code, r.content))
    else:
        print("--- Login Ok ---\n    Code %s"%(r.status_code))
        logger_debug.info("--- Login Ok ---\n    Code %s"%(r.status_code))

        cst = r.headers.get('cst')
        xsecuritytoken = r.headers.get('x-security-token') #X-Security-Token du compte par défaut

        urls.fullheaders = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'version':1, 'X-IG-API-KEY': personal.api_key, 'CST': cst, 'X-SECURITY-TOKEN': xsecuritytoken } #Création du fullheader pour les prochaines requetes avec Version:2
        
        urls.fullheaders_v2 = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'version':2, 'X-IG-API-KEY': personal.api_key, 'CST': cst, 'X-SECURITY-TOKEN': xsecuritytoken } #Création du fullheader pour les prochaines requetes avec Version:2

        urls.deleteheaders = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'version':1,  'X-IG-API-KEY': personal.api_key, 'CST': cst, 'X-SECURITY-TOKEN': xsecuritytoken, '_method': 'DELETE' } #Bug chez IG, donc ajout d'un header _method DELETE a defaut de pouvoir utiliser la directive DELETE
        
        urls.deleteheaders_v2 = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'version':2,  'X-IG-API-KEY': personal.api_key, 'CST': cst, 'X-SECURITY-TOKEN': xsecuritytoken, '_method': 'DELETE' } #Bug chez IG, donc ajout d'un header _method DELETE a defaut de pouvoir utiliser la directive DELETE avec Version:2
        body = r.json()

        lightstreamerEndpoint = body.get(u'lightstreamerEndpoint') #Recupére l'url d'accès à LS
        clientId = body.get(u'clientId') # Récupére le clientId
        currentAccountId = body.get(u'currentAccountId') #Récupére l'Id du compte actif
        accounts = body.get(u'accounts') # récupére le dictionnaire avec les comptes disponibles

        #Impression de la liste des sous-comptes
        if len(accounts) > 1:
            print("Sous-comptes :")
            for i in accounts:
                print("--> ID: %s - Name: %s - Type:%s - Preferred:%s" % (i.get(u'accountId'),i.get(u'accountName'),i.get(u'accountType'),i.get(u'preferred')))

        #Switching de compte si necessaire
        if currentAccountId != accounts[int(personal.account_nb)].get(u'accountId'):
            #print("Current et compte selectionne sont different, Il faut switch le compte avant de l'utiliser")
            #Il faut switcher le compte
            switchingbody = {u'accountId':accounts[int(personal.account_nb)].get(u'accountId'), u'defaultAccount':''}
            r = requests.put(urls.sessionurl, data=json.dumps(switchingbody), headers=urls.fullheaders, proxies=personal.proxies)
            if r.status_code != 200:
                print(" --- Switching Error ---\n    Erreur Code %s"%(r.status_code))
                logger_debug.info(" --- Switching Error ---\n    Erreur Code %s"%(r.status_code))
            else:
                print("--- Switching Ok ---\n    Vers le compte %s" % (accounts[int(personal.account_nb)].get(u'accountId')))
                logger_debug.info("--- Switching Ok ---\n    Vers le compte %s" % (accounts[int(personal.account_nb)].get(u'accountId')))
                xsecuritytoken = r.headers.get('x-security-token') #X-Security-Token du compte selectionné
                urls.fullheaders = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'version':1, 'X-IG-API-KEY': personal.api_key, 'CST': cst, 'X-SECURITY-TOKEN': xsecuritytoken } #MàJ du fullheader pour les prochaines requetes

        # Depending on how many accounts you have with IG the '0' may need to change to select the correct one (spread bet, CFD account etc)
        #Update with the user account choices.
        accountId = accounts[int(personal.account_nb)].get(u'accountId')
        accountName = accounts[int(personal.account_nb)].get(u'accountName')

        #Connexion LS
        client = igls.LsClient(lightstreamerEndpoint+"/lightstreamer/")
        client.on_state.listen(events.on_state)
        client.create_session(username=accountId, password='CST-'+cst+'|XST-'+xsecuritytoken, adapter_set='')

        #Binding sur les differents flux de stream et fonctions associés
        priceTable = igls.Table(client,
            mode=igls.MODE_MERGE,
            item_ids='MARKET:%s' % personal.epic,
            schema="OFFER BID",
        ) 
        
        priceTable.on_update.listen(events.processPriceUpdate)

        #Ajout DEPOSIT pour test
        balanceTable = igls.Table(client,
            mode=igls.MODE_MERGE,
            item_ids='ACCOUNT:'+accountId,
            schema='AVAILABLE_CASH PNL DEPOSIT',
        )

        balanceTable.on_update.listen(events.processBalanceUpdate)

        #Modif falex
        positionTable = igls.Table(client,
            mode=igls.MODE_DISTINCT,
            item_ids='TRADE:'+accountId,
            schema='OPU', #Je garde uniquement OPU pour avoir les updates de status des positions en cours
        )

        positionTable.on_update.listen(events.processPositionUpdate)

        #Ajout falex##
        tradeTable = igls.Table(client,
            mode=igls.MODE_DISTINCT,
            item_ids='TRADE:'+accountId,
            schema='CONFIRMS', #Je ne garde que CONFIRMS
        )

        tradeTable.on_update.listen(events.processTradeUpdate)

        pivots = calculatePivots() #Calcul les PP en Daily/formule classique

        globalvar.minDealSize, globalvar.currencyCode, globalvar.valueOfOnePip, globalvar.scalingFactor, globalvar.minNormalStoporLimitDistance, globalvar.minControlledRiskStopDistance = getMarketsDetails() # Récupére la taille min d'ouverture d'un ticket et la monnaie d'échange
        #DEBUG#
        #print("Main retour fonction getMarketsDetails ==>>\n    ", globalvar.minDealSize, globalvar.currencyCode, globalvar.valueOfOnePip, globalvar.scalingFactor, globalvar.minNormalStoporLimitDistance, globalvar.minControlledRiskStopDistance)
        #globalvar.currencyCode = EUR, AUD, USD, GBP, ...
        width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        WIN_SIZE = (width/4, height/1.3)

        window = gui_main.Window(None, pivots=pivots, title='L3 scalping - ' + globalvar.version + ' - ' + accountId + " - " + accountName + " - " + globalvar.epic_to_shortname_dict.get(personal.epic), currencyCode=globalvar.currencyCode, size = WIN_SIZE) #gui.epic_choices[gui.epic.GetCurrentSelection()])
        #window = gui.Window(None, pivots=[0,0,0,0,0,0,0], title='Trading IG')

        window.buy_button.Bind(wx.EVT_BUTTON, buy)
        window.sell_button.Bind(wx.EVT_BUTTON, sell)
        window.lot_size.Bind(wx.EVT_TEXT, window.update_sizelot)
        window.SL_point.Bind(wx.EVT_TEXT, window.update_SLpoint)
        window.TP_point.Bind(wx.EVT_TEXT, window.update_TPpoint)
        window.SL_currency.Bind(wx.EVT_TEXT, window.update_SLcurrency)
        window.is_Force_Open_box.Bind(wx.EVT_CHECKBOX, window.update_forceOpen)
        window.is_Keyboard_Trading_box.Bind(wx.EVT_CHECKBOX, window.update_keyboardtrading)
        window.openpositions_list.Bind(wx.EVT_LIST_ITEM_SELECTED, window.OnClick_openpositionslist)
        window.panel.Bind(wx.EVT_CHAR_HOOK, OnKeyPress) #Intercepte l'équivalent du key-down.
        window.closeAll_button.Bind(wx.EVT_BUTTON, CloseAllButton)
        window.is_Stop_Guaranteed_box.Bind(wx.EVT_CHECKBOX, window.update_stopGuaranteed)
        window.SLto0_button.Bind(wx.EVT_BUTTON, SLto0)
        window.TPto0_button.Bind(wx.EVT_BUTTON, TPto0)
        window.SLtoPRU_button.Bind(wx.EVT_BUTTON, SLtoPRU)
        window.closeAllepic_button.Bind(wx.EVT_BUTTON, CloseAllepicButton)
        events.window = window #Transmet la variable windows au module events sans passer par la directive globale

        events.get_openPositions() #Charge la liste des positions en stock à l'ouverture du programme
        
        #Ajout Guilux pour afficher le PNL Journalier
        pnlEuro,pnlPoints,nbTrades = events.getDailyPnl() #Calcul du PNL journalier
        window.update_pnlDaily(pnlEuro,pnlPoints,nbTrades)
        
        #Polling toutes les X secondes des caracteristique du contrat.
        pollingThread = threading.Thread(target=pollingMarketsDetails, args=(60,))
        pollingThread.start()
        

if __name__ == '__main__':

    ### logueur console ###
    ####on crée un log file par jour uniquement####
    base_log_file = os.getcwd() + '//Logs//'
    #today = datetime.datetime.now().strftime('%Y-%m-%d')
    today = time.strftime('%Y-%m-%d')
    log_file = base_log_file + 'Debug-' + str(today) + '.log'
    list_log_files = glob.glob(base_log_file + '*.log')
    if log_file in list_log_files:
        log_file = log_file
    else:
        log_file = base_log_file + 'Debug-' + str(today) + '.log'

    ####configuration du logger####
    logger_debug = logging.getLogger()
    debug_handler = logging.FileHandler(log_file)
    debug_formatter =logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    debug_handler.setFormatter(debug_formatter)
    logger_debug.addHandler(debug_handler)
    logger_debug.setLevel(logging.DEBUG)

    # Login Window
    app = wx.App()
    loging_window = gui_login.LogWindow(None,'L3 scalping V'+globalvar.version+' - Login')
    loging_window.btnConn.Bind(wx.EVT_BUTTON, main)
    app.MainLoop()



