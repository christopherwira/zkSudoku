import streamlit as st
import pandas as pd
import numpy as np
from typing import List
from utils import zokrates_utils, web3_utils
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="ZK-Sudoku Race",
    page_icon="🧩",
    layout="wide"
)

# --- Sudoku Data ---
# This is the public puzzle board. 0 represents an empty cell.
SUDOKU_PROBLEM = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

CONTRACT_ADDRESS = '0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9'

# --- Helper Functions ---

def get_solution_grid() -> List[List[int]]:
    """
    Retrieves the current state of the user's solution from Streamlit's session state.
    Initializes it if it doesn't exist.
    """
    if 'solution_grid' not in st.session_state:
        st.session_state.solution_grid = [row[:] for row in SUDOKU_PROBLEM]
    return st.session_state.solution_grid

def update_session_state():
    """Applies edits from the data_editor back to the main solution_grid in session state."""
    edits = st.session_state.sudoku_editor
    grid_to_update = st.session_state.solution_grid
    for row, changed_cols in edits.get("edited_rows", {}).items():
        for col_str, new_value in changed_cols.items():
            col = int(col_str)
            grid_to_update[row][col] = int(new_value or 0)

def refresh_winners_list():
    """Fetches and updates the winners list in the session state."""
    contract_name = "Zksudoku" # Assuming this is the name of your main contract
    if 'contract_instance' not in st.session_state:
        st.session_state.contract_instance = web3_utils.create_contract_instance('zksudoku', CONTRACT_ADDRESS, st.session_state.web3_instance)

    contract = st.session_state.contract_instance
    if contract:
        winner_count = contract.functions.winnerCount().call()
        st.session_state.winners = [contract.functions.winners(i).call() for i in range(winner_count)]
    else:
        st.session_state.winners = []


# --- Main Application UI ---

st.title("🧩 ZK-Sudoku Race")
st.markdown("Prove you've solved the Sudoku to win a prize from the smart contract!")

# Initialize web3 provider and winners list in session state
if 'web3_instance' not in st.session_state:
    st.session_state.web3_instance = web3_utils.create_http_provider('http://hardhat:8545')
if 'winners' not in st.session_state:
    st.session_state.winners = []


# --- Main Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("The Puzzle")
    st.write("Click directly on the white cells to enter your solution.")

    solution = get_solution_grid()
    display_list = [[num if num != 0 else None for num in row] for row in solution]
    df_display = pd.DataFrame(display_list)
    disabled_df = pd.DataFrame(SUDOKU_PROBLEM) != 0

    st.data_editor(
        df_display,
        use_container_width=True,
        height=500,
        disabled=disabled_df,
        key="sudoku_editor",
        on_change=update_session_state
    )

with col2:
    st.header("Your Status")
    st.button("Refresh Winners", on_click=refresh_winners_list)
    st.subheader("🏆 Winners")
    
    # Display winners from session state
    if st.session_state.winners:
        for i, winner in enumerate(st.session_state.winners):
            st.text(f"#{i+1}: {winner}")
    else:
        st.text("No winners yet. Be the first!")

    st.divider()

    st.subheader("Submit Your Solution")
    account_index = st.number_input("Select Your Account Index", min_value=0, max_value=9, step=1, key="account_index")
    
    if st.button("Generate Proof & Submit to Contract", type="primary"):
        solution_grid = get_solution_grid()
        
        st.write("Submitting the following solution:")
        st.json(solution_grid)
        
        try:
            with st.spinner("Generating proof... this may take a moment."):
                # 1. Create the JSON input for ZoKrates using the current grid state
                
                # 2. Generate the proof
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
                w3 = st.session_state.web3_instance
                contract_instance = web3_utils.create_contract_instance('zksudoku', CONTRACT_ADDRESS, w3)
                print(contract_instance)
                (proof, inputs) = zokrates_utils.parse_proof('zksudoku')
                account_index = int(st.session_state.account_index)
                tx_hash = contract_instance.functions.submitSolution(proof, inputs).transact({"from":w3.eth.accounts[account_index]})
                submit_tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                st.text(str(submit_tx_receipt))
                st.success("Proof generated and transaction submitted successfully! (Placeholder)")

        except Exception as e:
            st.error(f"An error occurred: {e}")
