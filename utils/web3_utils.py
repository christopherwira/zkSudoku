from web3 import Web3
from solcx import install_solc, compile_files, set_solc_version

def create_HTTP_provider(http_provider_url):
    w3 = Web3(Web3.HTTPProvider(http_provider_url))
    return w3


def compile_and_deploy_authentication_contract(zokrates_file_name : str, web3_http_provider, return_receipt: bool = False):
    install_solc('0.8.30')
    set_solc_version('0.8.30')
    path = {}
    path['scheme_name'] = zokrates_file_name
    path['class_name'] = zokrates_file_name.capitalize()
    path['contract_directory'] = 'contracts'
    compiled = compile_files(["contracts/Zksudoku.sol"], output_values=["abi", "bin"])
    output = compiled['{contract_directory}/{class_name}.sol:SudokuRace'.format(**path)]
    return output
    # compiled_web3_contract = web3_http_provider.eth.contract(abi=output['abi'], bytecode=output['bin'])
    # # We use the default account to send the transaction (e.g., the first account in the HD wallet)
    # tx_hash = compiled_web3_contract.constructor().transact()
    # tx_receipt = web3_http_provider.eth.wait_for_transaction_receipt(tx_hash)
    # deployed_web3_contract = web3_http_provider.eth.contract(address=tx_receipt.contractAddress, abi=output['abi'])
    # if return_receipt:
    #     return (deployed_web3_contract, tx_receipt)
    # return deployed_web3_contract