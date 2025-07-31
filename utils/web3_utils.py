from web3 import Web3
from solcx import install_solc, compile_files, set_solc_version_pragma
from .paths import get_contract_paths, PROJECT_ROOT
import os

def create_HTTP_provider(http_provider_url):
    w3 = Web3(Web3.HTTPProvider(http_provider_url))
    return w3


def compile_contract(contract_name : str):
    install_solc()
    set_solc_version_pragma('pragma solidity ^0.8.0;')
    paths = get_contract_paths(contract_name)
    relative_path = os.path.relpath(paths["source_file"], PROJECT_ROOT)
    compiled = compile_files([f"{paths["source_file"]}"], output_values=["abi", "bin"])
    output = compiled[f"{relative_path}:{contract_name}"]
    return output

def deploy_contract(contract_name : str, web3_http_provider : Web3.HTTPProvider, compiled_output):
    compiled_web3_contract = web3_http_provider.eth.contract(abi=compiled_output['abi'], bytecode=compiled_output['bin'])
    # We use the default account to send the transaction (e.g., the first account in the HD wallet)
    tx_hash = compiled_web3_contract.constructor().transact()
    tx_receipt = web3_http_provider.eth.wait_for_transaction_receipt(tx_hash)
    deployed_web3_contract = web3_http_provider.eth.contract(address=tx_receipt.contractAddress, abi=compiled_output['abi'])
    return (deployed_web3_contract, tx_receipt)