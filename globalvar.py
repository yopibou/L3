# -*- coding:utf-8 -*-

#Fichier de définition/stockage des variables globales du programme.
import collections

version = "1.16"

#Variables Instrument
minDealSize = None #Affectation de la valeur à la connexion
currencyCode = None #Monnaie utilise par l'epic
valueOfOnePip = None #Valeur en monnaie d'un pip
scalingFactor = None #Valeur du facteur d'échelle
spread = None  #Valeur du spread
minNormalStoporLimitDistance = None #Distance en point/pips du Stop-Normal à l'ouverture
minControlledRiskStopDistance = None #Distance en point/pips du Stop-Garantie à l'ouverture

########################################
#V1 du dictionnaire de position ouverte
#dict_openposition = collections.OrderedDict() #Dictionnaire avec la référence du dealID comme "Key" et value une liste avec les éléments[epic, size, direction, level, TP, SL]
########################################
#V2 du dictionnaire de position ouverte
# Sous la forme { "dealId": { "epic":'', "size":'', "direction":'', "open_level":'', "limit_level":'', "stop_level":'', "pnl":''}, "dealId" : { ... }}
dict_openposition = collections.OrderedDict()
list_key = ["epic", "size", "direction", "open_level", "limit_level", "stop_level", "pnl"] #List pour ordonner les key des postions

#Variable "Ticket"
requestDealSize = 1.51
dealSizeDelta = 0 #Init à 0
isForceOpen = True
SLpoint = ''
TPpoint = ''
SLcurrency = ''

#Variable Programme
isStopGuaranteed = False

isKeyBoardTrading = False #Positionné à false pour forcer l'utilisateur à cliquer sur la case pour ne pas passer des trades

epic_dict = { 
                    "Japon 225 au comptant (Mini-contrat 1$)" : "IX.D.NIKKEI.IFM.IP",
                    "Australie 200 au comptant (Mini-contrat 5$A)" : "IX.D.ASX.IFM.IP",
                    "EU Stocks 50 au comptant (Mini-Contrat 2E)"	: "IX.D.STXE.IFM.IP",
                    "FTSE 100 au comptant (Contrat 1E)" : "IX.D.FTSE.IFE.IP",
                    "FTSE 100 au comptant (Mini-contrat 2GBP)" : "IX.D.FTSE.IFM.IP",
                    "France 40 au comptant (Mini-contrat 1E)" : "IX.D.CAC.IMF.IP",
                    "Allemagne 30 au comptant (Mini-contrat 5E)" : "IX.D.DAX.IMF.IP",
                    "Allemagne 30 au comptant (contrat PLEIN 25E)" : "IX.D.DAX.IDF.IP",
                    "Espagne 35  au comptant (Mini-contrat 2E)" : "IX.D.IBEX.IFM.IP",
                    "US Tech 100 au comptant (Mini-contrat 20$)" : "IX.D.NASDAQ.IFM.IP",
                    "US 500 au comptant (Mini-contrat 50$)" : "IX.D.SPTRD.IFM.IP",
                    "US 500 au comptant (Contrat 1E)" : "IX.D.SPTRD.IFE.IP",
                    "Wall Street au comptant (Mini-contrat 2$)" : "IX.D.DOW.IMF.IP",
                    "Wall Street au comptant (Contrat 1E)" : "IX.D.DOW.IFE.IP",
                    "FX au comptant (mini) AUD/USD"	: "CS.D.AUDUSD.MINI.IP",
                    "FX au comptant (mini) EUR/CHF"	: "CS.D.EURCHF.MINI.IP",
                    "FX au comptant (mini) EUR/GBP"	: "CS.D.EURGBP.MINI.IP",
                    "FX au comptant (mini) EUR/JPY"	: "CS.D.EURJPY.MINI.IP",
                    "FX au comptant (mini) EUR/USD"	: "CS.D.EURUSD.MINI.IP",
                    "FX au comptant (mini) GBP/USD"	: "CS.D.GBPUSD.MINI.IP",
                    "FX au comptant (mini) USD/CAD"	: "CS.D.USDCAD.MINI.IP",
                    "FX au comptant (mini) USD/CHF"	: "CS.D.USDCHF.MINI.IP",
                    "FX au comptant (mini) USD/JPY"	: "CS.D.USDJPY.MINI.IP",
                    "FX au comptant (mini) CHF/JPY"	: "CS.D.CHFJPY.MINI.IP",
                    "FX au comptant (mini) EUR/CAD"	: "CS.D.EURCAD.MINI.IP",
                    "FX au comptant (mini) GBP/JPY"	: "CS.D.GBPJPY.MINI.IP",
                    "FX au comptant (mini) AUD/JPY"	: "CS.D.AUDJPY.MINI.IP",
                    }
#Dictionnaire pour afficher des noms court et inteligible à place de l'epic //A COMPLETER
epic_to_shortname_dict = {
                    "IX.D.ASX.IFM.IP" : "miniAustralie200(5AUD)",
                    "IX.D.STXE.IFM.IP" : "miniEU50(2E)",
                    "IX.D.FTSE.IFE.IP" : "miniFTSE100(1E)",
                    "IX.D.FTSE.IFM.IP" : "miniFTSE100(2GBP)",
                    "IX.D.CAC.IMF.IP" : "miniCAC40(1E)",
                    "IX.D.DAX.IMF.IP" : "miniDAX30(5E)",
                    "IX.D.IBEX.IFM.IP" : "miniES35(2E)",
                    "IX.D.NASDAQ.IFM.IP" : "miniUSTech100(20$)",
                    "IX.D.SPTRD.IFM.IP" : "miniSP500(50$)",
                    "IX.D.SPTRD.IFE.IP" : "miniSP500(1E)",
                    "IX.D.DOW.IMF.IP" : "miniDJIA30(2$)",
                    "IX.D.DOW.IFE.IP" : "miniDJIA30(1E)",
                    "IX.D.DAX.IDF.IP" : "DAX30(25E)",					
                    "CS.D.AUDUSD.MINI.IP" : "mini AUD/USD",
                    "CS.D.EURCHF.MINI.IP" : "mini EUR/CHF",
                    "CS.D.EURGBP.MINI.IP" : "mini EUR/GBP",
                    "CS.D.EURJPY.MINI.IP" : "mini EUR/JPY",
                    "CS.D.EURUSD.MINI.IP" : "mini EUR/USD",
                    "CS.D.GBPUSD.MINI.IP" : "mini GBP/USD",
                    "CS.D.USDCAD.MINI.IP" : "mini USD/CAD",
                    "CS.D.USDCHF.MINI.IP" : "mini USD/CHF",
                    "CS.D.USDJPY.MINI.IP" : "mini USD/JPY",
                    "CS.D.CHFJPY.MINI.IP" : "mini CHF/JPY",
                    "CS.D.EURCAD.MINI.IP" : "mini EUR/CAD",
                    "CS.D.GBPJPY.MINI.IP" : "mini GBP/JPY",
                    "CS.D.AUDJPY.MINI.IP" : "mini AUD/JPY",
                    }
