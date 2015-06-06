import personal

def set_urls():

    global sessionurl, neworderurl, closeorderurl, checkorderurl, positionsurl, pricesurl, marketsurl, headers, payload, updateorderurl, transactionhistoryurl, confirmsurl

    if personal.is_demo:
        ig_host="demo-api.ig.com"
    else:
        ig_host="api.ig.com"

    sessionurl = "https://%s/gateway/deal/session" % ig_host
    neworderurl = 'https://%s/gateway/deal/positions/otc' % ig_host
    closeorderurl = 'https://%s/gateway/deal/positions/otc' % ig_host
    checkorderurl = 'https://%s/gateway/deal/confirms/' % ig_host
    positionsurl = 'https://%s/gateway/deal/positions' % ig_host
    pricesurl = 'https://' + ig_host + '/gateway/deal/prices/%s/%s/2'
    marketsurl = 'https://'+ ig_host + '/gateway/deal/markets/%s'
    updateorderurl = 'https://' + ig_host + '/gateway/deal/positions/otc/%s'
    transactionhistoryurl = 'https://' + ig_host + '/gateway/deal/history/transactions/ALL/%s/%s'
    confirmsurl = 'https://'+ ig_host + '/gateway/deal/confirms/%s'

    headers = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'version':1, 'X-IG-API-KEY': personal.api_key}
    headers_v2 = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'version':2, 'X-IG-API-KEY': personal.api_key}
    payload = {'identifier': personal.username, 'password': personal.password.decode('base64')}

