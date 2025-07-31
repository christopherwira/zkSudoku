import subprocess
import shlex
import os
from typing import List, Dict, Tuple
from .paths import get_zokrates_paths, CONTRACT_DIR, ZOKRATES_STDLIB_PATH

def _snake_to_pascal_case(snake_case_string: str) -> str:
    """Converts a snake_case string to PascalCase.
    
    Example: 'general_zksudoku' -> 'GeneralZksudoku'
    """
    parts = snake_case_string.split('_')
    return "".join(part.capitalize() for part in parts)

def run_command(command: str, byte_input: bytes = None) -> str:
    """A robust wrapper for running subprocess commands."""
    try:
        process = subprocess.run(
            shlex.split(command),
            input=byte_input,
            capture_output=True,
            check=True,
            text=True
        )
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"--- COMMAND FAILED ---")
        print(f"Command: '{e.cmd}'")
        print(f"Return Code: {e.returncode}")
        
        if e.stdout:
            print("\n--- STDOUT ---")
            print(e.stdout.strip())
        if e.stderr:
            print("\n--- STDERR ---")
            print(e.stderr.strip())
        raise e

def compile_zokrates_script(zokrates_file_name: str, debug: bool = False) -> int:
    """Compiles a .zok file and returns the circuit size."""
    paths = get_zokrates_paths(zokrates_file_name)
    
    # Use os.makedirs for creating directories. It's safer than os.system.
    os.makedirs(paths['build_dir'], exist_ok=True)
    
    zokrates_compile_command = (
        f"zokrates compile "
        f"-s {paths['abi_file']} "
        f"-o {paths['out_file']} "
        f"-r {paths['r1cs_file']} "
        f"--stdlib-path {ZOKRATES_STDLIB_PATH} "
        f"-i {paths['source_file']}"
        f"{' --debug' if debug else ''}"
    )

    stdout_string = run_command(zokrates_compile_command)
    circuit_size = int(stdout_string.split(' ')[-1].replace('\n',''))
    return circuit_size

def generate_proving_verification_key_with_trusted_setup(zokrates_file_name: str):
    """Generates the proving and verification keys."""
    paths = get_zokrates_paths(zokrates_file_name)
    
    os.makedirs(paths['key_dir'], exist_ok=True)
    
    zokrates_setup_command = (
        f"zokrates setup "
        f"-i {paths['out_file']} "
        f"--backend bellman "
        f"--proving-key-path {paths['proving_key_file']} "
        f"--verification-key-path {paths['verification_key_file']}"
    )
    run_command(zokrates_setup_command)

def check_keys_size(zokrates_file_name: str) -> Tuple[int, int]:
    """Checks and prints the size of the generated keys."""
    paths = get_zokrates_paths(zokrates_file_name)
    
    pk_size = os.path.getsize(paths['proving_key_file'])
    vk_size = os.path.getsize(paths['verification_key_file'])
    
    print(f"Proving Key Size in Bytes: {pk_size:,}")
    print(f"Verification Key Size in Bytes: {vk_size:,}")
    return (pk_size, vk_size)

def generate_proof_from_json_input(zokrates_file_name: str, zokrates_json_input: bytes):
    """Generates a witness and a proof based on user input."""
    paths = get_zokrates_paths(zokrates_file_name)

    os.makedirs(paths['proof_dir'], exist_ok=True)

    # Generating witness from input.json      
    zokrates_compute_witness_command = (
        f"zokrates compute-witness "
        f"-s {paths['abi_file']} "
        f"-i {paths['out_file']} "
        f"--circom-witness {os.path.join(paths['build_dir'], 'out.wtns')} "
        f"-o {paths['witness_file']} "
        f"--verbose --abi "
        f"--stdin"
    )
    run_command(zokrates_compute_witness_command, zokrates_json_input)
    
    # Generating proof from witness
    zokrates_generate_proof_command = (
        f"zokrates generate-proof "
        f"--backend bellman "
        f"-i {paths['out_file']} "
        f"-w {paths['witness_file']} "
        f"-p {paths['proving_key_file']} "
        f"-j {paths['proof_json_file']}"
    )
    run_command(zokrates_generate_proof_command)

def verify_proof(zokrates_file_name: str) -> bool:
    """Verifies a generated proof using the verification key."""
    paths = get_zokrates_paths(zokrates_file_name)
    zokrates_verify_command = (
        f"zokrates verify "
        f"-v {paths['verification_key_file']} "
        f"-j {paths['proof_json_file']}"
    )
    try:
        stdout = run_command(zokrates_verify_command)

        # ZoKrates verify command outputs "PASSED" on success
        return "PASSED" in stdout
    except subprocess.CalledProcessError:
        # The run_command function already prints detailed errors
        return False
    
def generate_verification_contract_from_verification_key(zokrates_file_name: str):
    """Generate the verification contract using the verification key."""
    paths = get_zokrates_paths(zokrates_file_name)
    generated_dir = os.path.join(CONTRACT_DIR, "generated")
    os.makedirs(generated_dir, exist_ok=True)

    pascal_case_name = _snake_to_pascal_case(zokrates_file_name)
    contract_name = f"{pascal_case_name}Verifier.sol"
    verifier_contract_path = os.path.join(generated_dir, contract_name)

    zokrates_verify_command = (
        f"zokrates export-verifier "
        f"-i {paths['verification_key_file']} "
        f"-o {verifier_contract_path}"
    )
    run_command(zokrates_verify_command)
    