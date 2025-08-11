# tests/test_full_flow.py

import unittest
import json
from web3.exceptions import ContractLogicError

# Use absolute imports, as your environment is configured for it
from utils import zokrates_utils, web3_utils

class TestFullZKSudokuFlow(unittest.TestCase):

    # Class-level variables to share state between tests
    w3 = None
    contract = None
    proof = None
    inputs = None

    @classmethod
    def setUpClass(cls):
        """Set up the environment once for all tests."""
        print("\n--- Setting up Web3 Connection ---")
        cls.w3 = web3_utils.create_http_provider('http://hardhat:8545')
        cls.assertTrue(cls.w3.is_connected(), "Failed to connect to Hardhat node")
        print("Web3 connection successful.")

    def test_1_compile_and_setup(self):
        """Tests the compilation and trusted setup of the ZoKrates circuit."""
        print("\n--- Testing Step 1: Compile & Setup ---")
        circuit_size = zokrates_utils.compile_zokrates_script('zksudoku')
        self.assertGreater(circuit_size, 0, "Circuit compilation failed or size is zero.")
        print(f"Circuit compiled successfully (Size: {circuit_size}).")
        
        zokrates_utils.generate_proving_verification_key_with_trusted_setup('zksudoku')
        (pk_size, vk_size) = zokrates_utils.check_keys_size('zksudoku')
        self.assertGreater(pk_size, 0, "Proving key was not generated.")
        self.assertGreater(vk_size, 0, "Verification key was not generated.")
        print("Proving and verification keys generated successfully.")

    def test_2_generate_and_verify_proof(self):
        """Tests off-chain proof generation and verification."""
        print("\n--- Testing Step 2: Generate & Verify Proof ---")
        zksudoku_dict = [
            [
                [5, 3, 4, 6, 7, 8, 9, 1, 2],
                [6, 7, 2, 1, 9, 5, 3, 4, 8],
                [1, 9, 8, 3, 4, 2, 5, 6, 7],
                [8, 5, 9, 7, 6, 1, 4, 2, 3],
                [4, 2, 6, 8, 5, 3, 7, 9, 1],
                [7, 1, 3, 9, 2, 4, 8, 5, 6],
                [9, 6, 1, 5, 3, 7, 2, 8, 4],
                [2, 8, 7, 4, 1, 9, 6, 3, 5],
                [3, 4, 5, 2, 8, 6, 1, 7, 9]
            ],
            [
                [5, 3, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 9, 5, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [8, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 8, 0, 3, 0, 0, 1],
                [7, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 1, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 9]
            ]]

        zksudoku_string_dict = [[[str(num) for num in row] for row in grid] for grid in zksudoku_dict]

        zokrates_utils.generate_proof_from_json_input('zksudoku', json.dumps(zksudoku_string_dict))
        
        is_valid = zokrates_utils.verify_proof('zksudoku')
        self.assertTrue(is_valid, "Off-chain proof verification failed.")
        print("Proof generated and verified successfully off-chain.")

    def test_3_deploy_contract(self):
        """Tests contract compilation and deployment."""
        print("\n--- Testing Step 3: Deploy Contract ---")
        zokrates_utils.generate_verification_contract_from_verification_key('zksudoku')
        print("Verifier contract exported.")
        
        sudoku_problem_flat = [num for row in [
            [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ] for num in row]
        
        prize_pool_wei = self.w3.to_wei(30, 'ether')
        
        (contract, tx_receipt, _) = web3_utils.compile_and_deploy(
            self.w3, 
            'Zksudoku', 
            sudoku_problem_flat, 
            value=prize_pool_wei
        )
        
        self.assertIsNotNone(contract.address, "Contract deployment failed.")
        TestFullZKSudokuFlow.contract = contract
        print(f"Contract deployed successfully at {contract.address}.")

    def test_4_submit_solution_to_contract(self):
        """Tests submitting a valid proof to the smart contract."""
        print("\n--- Testing Step 4: Submit On-Chain Solution ---")
        self.assertIsNotNone(self.contract, "Contract not deployed, skipping test.")
        
        (proof, inputs) = zokrates_utils.parse_proof('zksudoku')
        
        initial_balance = web3_utils.get_account_balance(self.w3, 0)
        
        tx_hash = self.contract.functions.submitSolution(proof, inputs).transact({"from": self.w3.eth.accounts[0]})
        submit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        self.assertEqual(submit_tx_receipt.status, 1, "Transaction failed.")
        print("Solution submitted successfully to the contract.")
        
        final_balance = web3_utils.get_account_balance(self.w3, 0)
        self.assertGreater(final_balance, initial_balance, "Prize was not awarded correctly.")
        print("Prize awarded and balance updated.")

if __name__ == '__main__':
    unittest.main()