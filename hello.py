from utils import zokrates_utils,web3_utils
import json

circuit_size = zokrates_utils.compile_zokrates_script('zksudoku')
print(circuit_size)
zokrates_utils.generate_proving_verification_key_with_trusted_setup('zksudoku')
zokrates_utils.check_keys_size('zksudoku')
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

zokrates_utils.generate_proof_from_json_input(
    'zksudoku', json.dumps(zksudoku_string_dict))
print(zokrates_utils.verify_proof('zksudoku'))
zokrates_utils.generate_verification_contract_from_verification_key('zksudoku')
w3 = web3_utils.create_http_provider('http://hardhat:8545')
prize_pool_eth = w3.to_wei(0.3, 'ether')
(contract, tx_receipt, _) = web3_utils.compile_and_deploy(w3, 'zksudoku'.capitalize(), [num for row in zksudoku_dict[1] for num in row], value=prize_pool_eth)
print(contract.functions.abi)