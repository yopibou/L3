# -*- coding:utf-8 -*-

import requests
import json
import logging
import time

import urls
import personal
#import main

## Variables global
import globalvar

###   Logger
###logger = logging.getLogger("quotes")
###hdlr = logging.FileHandler('Logs/quotes-'+time.strftime("%d-%M-%Y")+'.log')
###formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
###hdlr.setFormatter(formatter)
###logger.addHandler(hdlr)
###logger.setLevel(logging.INFO)

# Tell the user when the Lighstreamer connection state changes
def on_state(state):
    print state

# Process à lighstreamer price update
def processPriceUpdate(item, myUpdateField):
    ##logger.info(str(myUpdateField))##Mise en sommeil du logger de flux LS

    bid, ask = myUpdateField
    sum_point = 0
    point_profit = 0
    ####calcul du pnl pour chaque pos de l'epic actif####
    for dealId in globalvar.dict_openposition:
        epic = globalvar.dict_openposition.get(dealId).get('epic')                         # on récupère l'epic
        direction = globalvar.dict_openposition.get(dealId).get('direction')               # on récupère le sens pour chaque pos
        open_level = globalvar.dict_openposition.get(dealId).get('open_level')             # on récupère l'open pour chaque pos
        size = globalvar.dict_openposition.get(dealId).get('size')                         # on récupère la size pour chaque pos
        ####calcul pnl en points de chaque position Exclusion des lignes qui ne sont pas dans bon epic####
        if (epic == personal.epic):
            if (direction == 'BUY'):
                point_profit = round((float(ask) - float(open_level)) * globalvar.scalingFactor * size,1) #Ajout du scalingFactor * la taille
            elif (direction == 'SELL'):
                point_profit = round((float(open_level) - float(bid)) * globalvar.scalingFactor * size,1) #Ajout du scalingFactor * la taille
            sum_point = sum_point + point_profit
        else:
            point_profit = 'N/A'
        globalvar.dict_openposition[dealId]['pnl'] = point_profit
    #print("Après la boucle For du dico de position")
    
    window.update_price(bid, ask, sum_point)

# Process an update of the users trading account balance
def processBalanceUpdate(item, myUpdateField):
    #print("--- processBalanceUpdate ---")
    #print(myUpdateField)
    balance, pnl, deposit = myUpdateField
    #Deplacement du code qui compte le nb de pos et la taille agregee des lots pour l'epic donne dans processPositionUpdate
    #Ajout deposit
    window.update_balance(balance, pnl, deposit)

# Process an update when an OPU message occured
def processPositionUpdate(item, myUpdateField):
    #_# Fonction appelé sur reception d'un LS OPU #_#
    #print("--- processPositionUpdate ----")

    #DEBUG#
    #print("    message OPU : \n    %s"%myUpdateField)
    #print ("Type %s"%type(myUpdateField))

    if myUpdateField[0] != None:
        opu = next(json.loads(field) for field in myUpdateField if field != None) #maroxe + falex
        opu_ordo = [opu.get(u'status'), opu.get(u'direction'), opu.get(u'size'), opu.get(u'level'), opu.get(u'limitLevel'), opu.get(u'stopLevel'), opu.get(u'guaranteedStop'), opu.get(u'limitDistance'), opu.get(u'stopDistance'), opu.get(u'dealStatus'), opu.get(u'dealId'), opu.get(u'reason'), opu.get(u'epic'), opu.get(u'expiry'), opu.get(u'affectedDeals'), opu.get(u'dealReference')]
        window.add_OPUmessage(opu_ordo) #Envoi des evenements OPU dans la sous fenêtre OPU

        #Trois message 'status' à gerer :
        #'OPEN' = Ouverture d'un nouveau ticket : Size = taille de l'ouverture
        #'DELETED' = Fermeture d'un ticket existant : Size = Taille restante du ticket avant de tomber à Zéro. Message deleted = le ticket est complétement fermé il n'en reste plus rien.
        #'UPDATED' = MaJ du ticket (taille, SL, TP, trailling) : Size = Nouvelle taille du ticket avec ce qui reste.
        dealId = opu.get(u'dealId')
        if opu.get('status') == u'OPEN':
            #print("Ouverture position")
            #open_values = [opu.get(u'epic'), opu.get(u'size'), opu.get(u'direction'), opu.get(u'level'), opu.get(u'limitLevel'), opu.get(u'stopLevel')]
            #MàJ avec la v2 du dico
            open_values = {'epic':opu.get(u'epic'), 'size':opu.get(u'size'), 'direction':opu.get(u'direction'), 'open_level':opu.get(u'level'), 'limit_level':opu.get(u'limitLevel'), 'stop_level':opu.get(u'stopLevel'), 'pnl':'N/A'}
            globalvar.dict_openposition.update({dealId:open_values})#Enregistrement de la position dans le dico
            window.set_openpositions(globalvar.dict_openposition) # Envoi le dictionnaire à afficher
            pru = PRU(personal.epic)
            window.update_pru(pru)
            update_countTicket()
        elif opu.get('status') == u'DELETED':
            #print("Fermeture position")
            try:
                del globalvar.dict_openposition[dealId]
            except KeyError:
                print("Erreur MaJ dico positions ouvertes")
                pass
            #print(globalvar.dict_openposition)
            window.set_openpositions(globalvar.dict_openposition) # Envoi le dictionnaire à afficher
            pru = PRU(personal.epic)
            window.update_pru(pru)
            update_countTicket()

			#Guilux modif pouir afficher le PNL Journalier
            pnlEuro,pnlPoints,nbTrades = getDailyPnl() #Calcul du PNL journalier
            window.update_pnlDaily(pnlEuro,pnlPoints,nbTrades)

        elif opu.get('status') == u'UPDATED':
            #print("Mise a jour ticket")
            #udpate_values = [opu.get(u'epic'), opu.get(u'size'), opu.get(u'direction'), opu.get(u'level'), opu.get(u'limitLevel'), opu.get(u'stopLevel')]
            #MàJ avec la v2 du dico
            udpate_values = {'epic':opu.get(u'epic'), 'size':opu.get(u'size'), 'direction':opu.get(u'direction'), 'open_level':opu.get(u'level'), 'limit_level':opu.get(u'limitLevel'), 'stop_level':opu.get(u'stopLevel'), 'pnl':'N/A'}
            globalvar.dict_openposition[dealId] = udpate_values #MàJ du dico
            #print(globalvar.dict_openposition)
            window.set_openpositions(globalvar.dict_openposition) # Envoi le dictionnaire à afficher
            pru = PRU(personal.epic)
            window.update_pru(pru)
            update_countTicket()
            
		    #Guilux modif pouir afficher le PNL Journalier
            pnlEuro,pnlPoints,nbTrades = getDailyPnl() #Calcul du PNL journalier
            window.update_pnlDaily(pnlEuro,pnlPoints,nbTrades)
        else:
            print("Autre status non gere : %s",opu.get('status'))
    #else:
    #    print("   message OPU = None ou vide")

    #print ("---Fin---")

def update_countTicket():
    #print("--- update_countTicket ---")
    #V1.14.2 : Correction en mode calcul local pour ne pas génére de requete REST "inutile" en cas de trop nombreux messages
    # Externalisation de la fonction
    #Déplacement de cette requete, dans PositionUpdate sinon je genere trop de requete /position (et ca ne sert a rien en dehors des modifications)
    #r = requests.get(urls.positionsurl, headers=urls.fullheaders, proxies=personal.proxies)
    #s = json.loads(r.content).get("positions")
    #Ajout Falex pour l'epic en cours je somme la taille des positions Sell et Buy
    sizeBuy = 0
    sizeSell = 0
    nb_ticket = 0
    for dealId in globalvar.dict_openposition:
        epic = globalvar.dict_openposition.get(dealId).get('epic')    # on récupère l'epic pour chaque pos
        direction = globalvar.dict_openposition.get(dealId).get('direction')    # on récupère le sens pour chaque pos
        size = globalvar.dict_openposition.get(dealId).get('size')    # on récupère la taille pour chaque pos
        #d = p.get("position").get("direction")
        #s = p.get("position").get("dealSize")
        #e = p.get("market").get("epic")
        if (epic == personal.epic):
            if direction == "BUY":
                sizeBuy += size
                nb_ticket += 1
            elif direction == "SELL":
                sizeSell += size
                nb_ticket += 1
    window.update_pos(nb_ticket, sizeBuy, sizeSell)
    #print ("---Fin---")    
    
#Ajout falex
def processTradeUpdate(item, myUpdateField):
    #_# Fonction appelé sur reception d'un LS CONFIRMS #_#
    #DEBUG#
    #print("--- processTradeUpdate ---")
    #print("globalvar.dealSizeDelta = ",globalvar.dealSizeDelta)
    #print("myUpdateField ==>>> ",myUpdateField)

    if myUpdateField[0] != None:
        #DEBUG#
        #print("myUpdateField ==>>>", myUpdateField)
        message = next(json.loads(field) for field in myUpdateField if field != None)
        direction = message.get(u'direction')
        status = message.get(u'status')
        dealId = message.get(u'dealId')
        dealReference = message.get(u'dealReference')
        dealStatus = message.get(u'dealStatus')
        reason = message.get(u'reason')
        #if message.get(u'affectedDeals') != None:
        if dealStatus == u'ACCEPTED':
            #Suppression d'un bout de ticket si la taille demandé est inférieur à la taille min du contrat
            for f in message.get(u'affectedDeals'):
                affDealsId = f.get(u'dealId')
                affstatus = f.get(u'status')
                #if (affDealsId == dealId and affstatus == u'OPENED' and globalvar.dealSizeDelta > 0): #Jusqu'à présent dealId et AffDealsId avaient la même référence à l'ouverture.
                if (affstatus == u'OPENED' and globalvar.dealSizeDelta > 0): #Modification des conditions d'entrée, si status OPENED et globalvar.dealSizeDelta > 0
                    #DEBUG#
                    #print("Je sors %s de la position" % globalvar.dealSizeDelta)
                    body = {"dealId": affDealsId, "direction": "SELL", "size": globalvar.dealSizeDelta, "orderType": "MARKET"} #UPDATE avec le affected Deal Id
                    if direction == "SELL": #ajustement de la direction dans l'ordre DELETE en fonction du sens d'ouverture
                        body['direction'] = "BUY"
                    #DEBUG#
                    #print("data ", body)
                    #print("headers ", urls.deleteheaders)
                    r = requests.post(urls.closeorderurl, data=json.dumps(body), headers=urls.deleteheaders, proxies=personal.proxies)
        else:
            #Problème dans l'ordre, création d'un dictionnaire similaire à OPU pour l'envoyer à l'affichage dans le fenêtre d'évènement
            opu_ordo = [dealStatus, reason]
            window.add_OPUmessage(opu_ordo) #Envoi des evenements OPU dans la sous fenêtre OPU
        #print("Post DELETE Status code -> ", r.status_code)
    #print("----Fin----")

 # Process the set the openposition from an empty list, the number of tick and aggregate lot for the current epic
def get_openPositions():
    #print("--- get_openPositions ---")

    r = requests.get(urls.positionsurl, headers=urls.fullheaders, proxies=personal.proxies)
    s = json.loads(r.content).get("positions")
    print("--- get_openPositions ---\n    Code %s"%(r.status_code))
    globalvar.dict_openposition = {} ###Ajout 1.14.2
    sizeBuy = 0
    sizeSell = 0
    nb_ticket = 0
    for p in s:
        dealId = p.get("position").get("dealId")      #DealID
        d = p.get("position").get("direction")        #Sens
        s = p.get("position").get("dealSize")         #Taille du contrat
        ol = p.get("position").get("openLevel")       #Cours d'ouverture
        sl = p.get("position").get("stopLevel")       #SL
        ll = p.get("position").get("limitLevel")      #TP
        e = p.get("market").get("epic")               #sous-jacent
        if (e == personal.epic):
            if d == "BUY":
                sizeBuy += s
                nb_ticket += 1
            elif d == "SELL":
                sizeSell += s
                nb_ticket += 1
        #globalvar.dict_openposition.update({dealId:[e,s, d, ol, ll, sl]}) #Ajout position dans le dictionnaire "dealdId":[epic, size, direction, openLevel, TP, SL]`
        #MàJ avec la v2 du dico
        globalvar.dict_openposition.update({dealId:{"epic":e, "size":s, "direction":d, "open_level":ol, "limit_level":ll, "stop_level":sl, "pnl":'N/A'}})
    window.update_pos(nb_ticket, sizeBuy, sizeSell)
    #print("Envoi de =>>>>>>>>>> ",globalvar.dict_openposition)
    window.set_openpositions(globalvar.dict_openposition) # Ok
    pru = PRU(personal.epic)
    window.update_pru(pru)
    #print ("---Fin---")

#Process de suppresion d'un ticket en fonction de son dealId, direction et taille.
def delete(dealId, direction, reqDealSize):
    #print("--- events.delete ---")
    print("Ticket %s a supprimer" %(dealId))

    body = {"dealId": dealId, "direction": "SELL", "size": reqDealSize, "orderType": "MARKET"}
    #print(body)
    if direction == "SELL": #ajustement de la direction dans l'ordre DELETE en fonction du sens d'ouverture
        body['direction'] = "BUY"

    r = requests.post(urls.closeorderurl, data=json.dumps(body), headers=urls.deleteheaders, proxies=personal.proxies)

    print("--- delete ---\n    Code %s"%(r.status_code))
    if r.status_code != 200: #Si message d'erreur alors on force le refresh des positions en local avec une R REST
        get_openPositions()
    #print("--- FIN : Events.delete ---")

def updateLimit(dealId, SLlevel, TPlevel):
    #DEBUG#
    print(" --- updateLimit ---")
    print("Ticket %s a updater SL = %s TP = %s" %(dealId, SLlevel, TPlevel))
    body = {"limitLevel":TPlevel, "stopLevel":SLlevel}
    r = requests.put(urls.updateorderurl % (dealId), data=json.dumps(body), headers=urls.fullheaders, proxies=personal.proxies)
    print("--- updateLimit ---\n    Code %s"%(r.status_code))
    #print("--- FIN : Events.updateLimit ---")

#### fonction que j'ai du mettre ici pour pouvoir l'utiliser dans main et events.
def PRU(epic):
    pru = 0
    size = 0
    for dealId in globalvar.dict_openposition:
        if globalvar.dict_openposition.get(dealId).get('epic') == epic:
            o = float(globalvar.dict_openposition.get(dealId).get('open_level'))
            s = globalvar.dict_openposition.get(dealId).get('size')
            pru = pru + (o*s)
            size = size + s
    try:
        pru = round(float(pru/size), 5) #Arrondi à 5 décimale
    except ZeroDivisionError:
        pru = None
    return pru

###Fonction dans main, déplacer dans events pour pouvoir être utilisé dans main et event sans imports de main dans events
def getDailyPnl():

    """ Fonction qui retourne le PNL en Euro et en points ainsi
    que le nombre de trades passés sur la journée   """

    pnlEuro=0.0         #PNL en Euro
    nbTrades=0          #Nombre de trades
    pnlPoints = 0.0       #PNL en points
    size=0.0

    daydate = time.strftime('%d-%m-%Y',time.localtime()) # recup de la date du jour
    #url = 'https://'+ urls.ig_host +'/gateway/deal/history/transactions/ALL/'+daydate+'/'+daydate #Formatage de l'url avec la date du jour
    r = requests.get(urls.transactionhistoryurl %(daydate, daydate), headers=urls.fullheaders, proxies=personal.proxies)
    s = json.loads(r.content).get(u'transactions')


    for gain in s:
       if gain.get(u'transactionType')=='ORDRE':   #On ne calcule que si le type de la transaction est "ordre"

        # Calcul du PNL Journalier en Euro
         b = gain.get(u'profitAndLoss') # on recupere le pnl de la transaction
         b = b[1:]                      # on supprime le 'E'
         b = b.replace(',','')          # on supprime la ',' ex 2,500.50 -> 2500.50
         pnlEuro += float(b)            # on additionne toutes les transactions

        # Calcul du nombre de point
         openLevel = gain.get(u'openLevel') #recupere opellevel
         closeLevel = gain.get(u'closeLevel') #recupere closelevel

         directionLevel =  gain.get(u'size') #recupere la taille pour avoir le sens (+ ou -)
         size = directionLevel[1:]
         directionLevel = directionLevel[:1] # split pour recuperer '+' ou '-'


         if directionLevel == '+' :         #si + la difference est close - open
            diffLevel = float(closeLevel) - float(openLevel)
            diffLevel = diffLevel * float(size)
            diffLevel = round(diffLevel,1)  # on arrondi pour ne pas avoir 0,2999999 point

         if directionLevel =='-':           #si - la difference est open-close
            diffLevel = float(openLevel) - float(closeLevel)
            diffLevel = diffLevel * float(size)
            diffLevel = round(diffLevel,1)  # on arrondi pour ne pas avoir 0,2999999 point


         #print str(diffLevel) +'('+directionLevel+''+size+')' + ' p: '+str(diffLevel)

         #on additionne les points (+ et-)
         pnlPoints += diffLevel

         # Incrementation du nombre de trades
         nbTrades+=1

    #renvoi des 3 variables (pnlEuro, pnlPoints, nbTrades)
    return pnlEuro,pnlPoints, nbTrades