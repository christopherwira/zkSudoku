import streamlit as st
import pandas as pd
import numpy as np
from typing import List
from utils import zokrates_utils, web3_utils
from web3.contract import Contract
import json

st.set_page_config(
    page_title='ZK-Sudoku',
    layout='wide'
)

st.title("ZK-Sudoku")
st.markdown("Proving ZK-Sudoku in a zero-knowledge manner.")

if 'web3_instance' not in st.session_state:
    st.session_state.web3_instance = web3_utils.create_http_provider('http://hardhat:8545')

def connect_to_contract():
    try:
        contract_address = st.session_state.contract_address
        if contract_address: # Prevent Empty String
            contract_instance = web3_utils.create_contract_instance('zksudoku', contract_address, st.session_state.web3_instance)
            st.session_state.contract_instance = contract_instance
    except Exception as e:
        st.error(f"Failed to connect to the smart contract. Ensure the address is correct. {e}")
        reset_contract_address()

def fetch_winners():
    contract = st.session_state.contract_instance
    if 'winners' not in st.session_state:
        winners = contract.functions.getWinners().call()
        st.session_state.winners = winners

def refresh_winners():
    contract = st.session_state.contract_instance
    winners = contract.functions.getWinners().call()
    st.session_state.winners = winners

def reset_contract_address():
    for key in st.session_state.keys():
        st.session_state.pop(key, None)

def reset_board_to_problem():
    st.session_state.pop('sudoku_board',None)

def update_session_state():
    """Applies edits from the data_editor back to the main solution_grid in session state."""
    edits = st.session_state.sudoku_editor
    grid_to_update = st.session_state.solution_grid
    for row, changed_cols in edits.get("edited_rows", {}).items():
        for col_str, new_value in changed_cols.items():
            col = int(col_str)
            grid_to_update[row][col] = int(new_value or 0)


if 'contract_instance' not in st.session_state:
    st.text("Please insert the smart contract address of your designated Sudoku Problem")
    st.text_input("Contract Address", key='contract_address', on_change=connect_to_contract)
else:
    st.text(f"Current Contract Address: {st.session_state.contract_instance.address}")
    st.button("Reset Address", on_click=reset_contract_address)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("The Puzzle")
        st.write("Click directly on the white cells to enter your solution.")
        contract_instance: Contract = st.session_state.contract_instance
        if 'sudoku_problem' not in st.session_state:
            sudoku_problem_flat_list = contract_instance.functions.getSudokuProblem().call()
            sudoku_problem = [sudoku_problem_flat_list[i:i + 9] for i in range(0, len(sudoku_problem_flat_list), 9)]
            st.session_state.sudoku_problem = sudoku_problem
        st.write(f"Problem in the Contract: {st.session_state.sudoku_problem}")
        if 'solution_grid' not in st.session_state:
            st.session_state.solution_grid = [row[:] for row in st.session_state.sudoku_problem]
        display_list = [[num if num != 0 else None for num in row] for row in st.session_state.solution_grid]
        df_display = pd.DataFrame(display_list)

        st.data_editor(
            df_display,
            use_container_width=True,
            height=500,
            key="sudoku_editor",
            on_change=update_session_state
        )
        st.button("Revert Board", on_click=reset_board_to_problem)
        st.text(f"Your Solution: {st.session_state.solution_grid}")
    with col2:
        st.subheader("🏆 Winners")
        fetch_winners()
        st.button("Refresh Winners", on_click=refresh_winners)
        for i, winner in enumerate(st.session_state.winners):
            if winner != '0x0000000000000000000000000000000000000000':
                st.text(f"#{i+1}: {winner}")
            else:
                st.text(f"#{i+1}: No Winner Yet")
        st.divider()

        st.subheader("Submit Your Solution")
        account_index = st.number_input("Select Your Account Index", min_value=0, max_value=9, step=1, key="account_index")
        
        if st.button("Generate Proof & Submit to Contract", type="primary"):
            solution_grid = st.session_state.solution_grid
            
            st.write("Submitting the following solution:")
            
            try:
                with st.spinner("Generating proof... this may take a moment."):
                    zksudoku_dict = [
                    st.session_state.solution_grid,
                    st.session_state.sudoku_problem]
                    zksudoku_string_dict = [[[str(num) for num in row] for row in grid] for grid in zksudoku_dict]
                    zokrates_utils.generate_proof_from_json_input('zksudoku', json.dumps(zksudoku_string_dict))
                    w3 = st.session_state.web3_instance
                    contract_instance = st.session_state.contract_instance
                    (proof, inputs) = zokrates_utils.parse_proof('zksudoku')
                    account_index = int(st.session_state.account_index)
                    tx_hash = contract_instance.functions.submitSolution(proof, inputs).transact({"from":w3.eth.accounts[account_index]})
                    submit_tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    st.text(str(submit_tx_receipt))
                    st.success("Proof generated and transaction submitted successfully! (Placeholder)")

            except Exception as e:
                st.error(f"An error occurred: {e}")