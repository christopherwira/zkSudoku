import os
from typing import Dict

# --- Base Project Directories ---
# Define the root of your project. We use os.path.abspath to get a full path.
# This makes the path resolution robust, no matter where you run your scripts from.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

CONTRACT_DIR = os.path.join(PROJECT_ROOT, 'contracts')
ZOKRATES_DIR = os.path.join(PROJECT_ROOT, 'zokrates')

# --- ZoKrates Specific Paths ---
ZOKRATES_SRC_DIR = os.path.join(ZOKRATES_DIR, 'src')
ZOKRATES_TEMP_DIR = os.path.join(ZOKRATES_DIR, 'temp')
ZOKRATES_STDLIB_PATH = '/opt/zokrates/stdlib/' # This is a system path, so it's absolute

def get_zokrates_paths(file_name: str) -> Dict[str, str]:
    """
    A centralized function to generate all necessary paths for a ZoKrates file.
    """
    base_temp_path = os.path.join(ZOKRATES_TEMP_DIR)
    
    paths = {
        'source_file': os.path.join(ZOKRATES_SRC_DIR, f"{file_name}.zok"),
        'build_dir': os.path.join(base_temp_path, 'builds', file_name),
        'key_dir': os.path.join(base_temp_path, 'keys', file_name),
        'proof_dir': os.path.join(base_temp_path, 'proofs', file_name),
    }

    # Add specific file paths based on the directory paths
    paths['abi_file'] = os.path.join(paths['build_dir'], 'abi.json')
    paths['out_file'] = os.path.join(paths['build_dir'], 'out')
    paths['r1cs_file'] = os.path.join(paths['build_dir'], 'out.r1cs')
    paths['witness_file'] = os.path.join(paths['proof_dir'], 'witness')
    paths['proving_key_file'] = os.path.join(paths['key_dir'], 'proving.key')
    paths['verification_key_file'] = os.path.join(paths['key_dir'], 'verification.key')
    paths['proof_json_file'] = os.path.join(paths['proof_dir'], 'proof_output.json')
    
    return paths

def get_contract_paths(contract_name: str) -> Dict[str, str]:
    """A centralized function for contract-related paths."""
    generated_dir = os.path.join(CONTRACT_DIR, "generated")
    artifacts_dir = os.path.join(CONTRACT_DIR, "artifacts")
    return {
        'source_file': os.path.join(CONTRACT_DIR, f"{contract_name}.sol"),
        'verifier_file': os.path.join(generated_dir, f"{contract_name}Verifier.sol"),
        'abi_file': os.path.join(artifacts_dir, f"{contract_name}.abi"),
        'bin_file': os.path.join(artifacts_dir, f"{contract_name}.bin"),
    }