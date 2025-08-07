import os, json
from typing import Tuple, Dict, Any, Optional
from decimal import Decimal

from web3 import Web3
from web3.providers.persistent import WebSocketProvider
from web3.contract import Contract
from web3.types import TxReceipt
from solcx import install_solc, compile_files, set_solc_version_pragma

# Import path helpers from your paths module
from .paths import get_contract_paths, PROJECT_ROOT

# --- Global variable to track if solc is installed ---
_solc_installed = False

def _ensure_solc_installed(version: str = '0.8.30'):
    """
    A helper function that ensures the Solidity compiler is installed,
    but only runs the installation once per session.
    """
    global _solc_installed
    if not _solc_installed:
        print(f"Installing Solidity compiler version {version}...")
        install_solc(version)
        set_solc_version_pragma(f'pragma solidity ^{version.rsplit(".", 1)[0]};')
        _solc_installed = True

def _save_contract_artifacts(contract_name: str, compiled_output: dict, paths: dict):
    """Saves the ABI and bytecode to the artifacts directory."""
    artifacts_dir = os.path.dirname(paths['abi_file'])
    os.makedirs(artifacts_dir, exist_ok=True)

    # Save the ABI as a JSON file
    with open(paths['abi_file'], 'w') as f:
        json.dump(compiled_output['abi'], f, indent=2)

    # Save the bytecode (binary)
    with open(paths['bin_file'], 'w') as f:
        f.write(compiled_output['bin'])


def compile_and_deploy(
    web3_instance: Web3,
    contract_name: str,
    *constructor_args: Any,
    value: int = 0
) -> Tuple[Contract, TxReceipt, Dict[str, Any]]:
    """
    A high-level function that compiles and deploys a smart contract in one go.

    Args:
        web3_instance: The connected Web3 instance.
        contract_name: The name of the contract to compile and deploy (e.g., "SudokuRace").
        *constructor_args: A variable number of arguments for the contract's constructor.
        value: The amount of ETH (in wei) to send with the deployment (for payable constructors).

    Returns:
        A tuple containing:
        - The deployed Web3 contract instance.
        - The transaction receipt.
        - The compiled output (ABI and bytecode).
    """
    # 1. Ensure compiler is ready and compile the contract
    _ensure_solc_installed()
    
    paths = get_contract_paths(contract_name)
    source_file_path = paths["source_file"]
    
    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"Contract source file not found at: {source_file_path}")

    compiled_sol = compile_files([source_file_path], output_values=["abi", "bin"])
    contract_key = next(iter(compiled_sol)) # Take the first key in the compiled_sol dictionary
    compiled_output = compiled_sol[contract_key]

    _save_contract_artifacts(contract_name, compiled_output, paths)

    # 2. Deploy the compiled contract
    contract = web3_instance.eth.contract(
        abi=compiled_output['abi'],
        bytecode=compiled_output['bin']
    )
    
    deployer_account = web3_instance.eth.accounts[0]

    tx_hash = contract.constructor(*constructor_args).transact({
        'from': deployer_account,
        'value': value
    })

    tx_receipt = web3_instance.eth.wait_for_transaction_receipt(tx_hash)
    
    deployed_contract = web3_instance.eth.contract(
        address=tx_receipt.contractAddress,
        abi=compiled_output['abi']
    )
    print(f"Contract '{contract_name}' deployed successfully at address: {tx_receipt.contractAddress}")
    
    return (deployed_contract, tx_receipt, compiled_output)


def create_http_provider(http_provider_url: str) -> Web3:
    """Creates and returns a Web3 HTTP provider instance."""
    return Web3(Web3.HTTPProvider(http_provider_url))

def create_contract_instance(contract_name: str, contract_address: str, web3_instance: Web3) -> Contract:
    paths = get_contract_paths(contract_name)
    with open(paths['abi_file'], 'r') as f:
        contract_abi = json.load(f)
    return web3_instance.eth.contract(abi=contract_abi, address=contract_address)

def get_account_balance(
    web3_instance: Web3, 
    account_index: int = 0
) -> Optional[Decimal]:
    """
    Fetches and returns the balance of a specific account in Ether.

    Args:
        web3_instance: The connected Web3 instance.
        account_index: The index of the account in the provider's list 
                       (defaults to the first account).

    Returns:
        The account balance as a Decimal object in Ether, or None if an error occurs.
    """
    try:
        account = web3_instance.eth.accounts[account_index]
        balance_wei = web3_instance.eth.get_balance(account)
        balance_eth = Web3.from_wei(balance_wei, 'ether')
        return balance_eth
    except IndexError:
        print(f"Error: Account with index {account_index} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None