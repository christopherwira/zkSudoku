from web3 import Web3

def create_HTTP_provider(http_provider_url):
    w3 = Web3(Web3.HTTPProvider(http_provider_url))
    return w3
