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

def deploy_contract(
    web3_provider: Web3, 
    compiled_output: dict, 
    *constructor_args, # Collects all positional arguments
    value: int = 0      # Optional: for payable constructors
):
    """
    Deploys a contract and waits for the receipt.
    This function is flexible and accepts any number of constructor arguments.

    Args:
        web3_provider: The connected Web3 instance.
        compiled_output: The dictionary containing the contract's 'abi' and 'bin'.
        *constructor_args: A variable number of arguments to pass to the contract's constructor.
        value: The amount of ETH (in wei) to send with the deployment (for payable constructors).

    Returns:
        A tuple containing the deployed contract instance and the transaction receipt.
    """
    contract = web3_provider.eth.contract(
        abi=compiled_output['abi'], 
        bytecode=compiled_output['bin']
    )
    
    # Use the first account provided by the node as the deployer
    deployer_account = web3_provider.eth.accounts[0]

    # Pass the collected constructor arguments directly to the constructor() call
    tx_hash = contract.constructor(*constructor_args).transact({
        'from': deployer_account,
        'value': value
    })

    tx_receipt = web3_provider.eth.wait_for_transaction_receipt(tx_hash)
    
    deployed_contract = web3_provider.eth.contract(
        address=tx_receipt.contractAddress, 
        abi=compiled_output['abi']
    )
    
    return (deployed_contract, tx_receipt)