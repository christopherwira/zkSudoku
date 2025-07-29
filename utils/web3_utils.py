from web3 import Web3
from solcx import install_solc, compile_files, set_solc_version

def create_HTTP_provider(http_provider_url):
    w3 = Web3(Web3.HTTPProvider(http_provider_url))
    return w3