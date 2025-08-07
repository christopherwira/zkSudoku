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

# --- Helper Functions ---

def get_solution_grid() -> List[List[int]]:
    """
    Retrieves the current state of the user's solution from Streamlit's session state.
    Initializes it if it doesn't exist.
    """
    if 'solution_grid' not in st.session_state:
        # Initialize the solution grid as a copy of the problem
        st.session_state.solution_grid = [row[:] for row in SUDOKU_PROBLEM]
    return st.session_state.solution_grid

# --- THE FIX ---
# This callback correctly handles the dictionary of edits provided by st.data_editor's state.
def update_session_state():
    """Applies edits from the data_editor back to the main solution_grid in session state."""
    # st.session_state.sudoku_editor contains a dictionary of edits, not a DataFrame.
    edits = st.session_state.sudoku_editor
    
    # The grid to modify is our master copy in the session state.
    grid_to_update = st.session_state.solution_grid

    # Apply any edits the user has made by iterating through the edits dictionary.
    for row, changed_cols in edits.get("edited_rows", {}).items():
        for col_str, new_value in changed_cols.items():
            col = int(col_str)
            # Ensure the new value is an integer, defaulting to 0 if empty/None.
            grid_to_update[row][col] = int(new_value or 0)

# --- Main Application UI ---

st.title("🧩 ZK-Sudoku Race")
st.markdown("Prove you've solved the Sudoku to win a prize from the smart contract!")
st.session_state.web3_instance = web3_utils.create_http_provider('http://hardhat:8545')

# --- Main Layout ---
col1, col2 = st.columns([2, 1]) # Create a 2/3 and 1/3 column layout

with col1:
    st.header("The Puzzle")
    st.write("Click directly on the white cells to enter your solution.")

    # Convert the current solution grid to a DataFrame for the editor
    solution = get_solution_grid()
    
    display_list = [[num if num != 0 else None for num in row] for row in solution]
    df_display = pd.DataFrame(display_list)

    # Create a boolean DataFrame to disable editing of the clue cells

    # --- THE NEW EDITABLE GRID ---
    # Use st.data_editor to create an interactive, editable grid.
    st.data_editor(
        df_display,
        use_container_width=True,
        height=500,
        key="sudoku_editor",
        # Use the on_change callback to reliably save edits.
        on_change=update_session_state
    )

with col2:
    st.header("Your Status")

    # --- Display Winners & Contract Info (Placeholder) ---
    st.subheader("🏆 Winners")
    st.text("1. 0x123...abc (Still open!)")
    st.text("2. 0x456...def (Still open!)")
    st.text("3. 0x789...ghi (Still open!)")

    st.divider()

    # --- Submission Section ---
    st.subheader("Submit Your Solution")
    st.text_input("Contract Address", key="contract_address")
    st.text_input("Account Index", key="account_index")
    
    if st.button("Generate Proof & Submit to Contract", type="primary"):
        solution_grid = get_solution_grid()
        
        st.write("Submitting the following solution:")
        # Display the final solution for confirmation
        st.json(solution_grid)
        
        
        with st.spinner("Generating proof... this may take a moment."):
            # --- TODO: INTEGRATION POINT ---
            # 1. Add a check here to verify the solution is complete and valid first.
            # 2. Call your zokrates_utils to generate the proof using the `solution_grid`.
            # 3. Call your web3_utils to parse the proof and call the smart contract.
            # 4. Handle the success or failure response.
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
            contract_instance = web3_utils.create_contract_instance('zksudoku', st.session_state.contract_address, w3)
            print(contract_instance)
            (proof, inputs) = zokrates_utils.parse_proof('zksudoku')
            account_index = int(st.session_state.account_index)
            tx_hash = contract_instance.functions.submitSolution(proof, inputs).transact({"from":w3.eth.accounts[account_index]})
            submit_tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            st.text(str(submit_tx_receipt))
            st.success("Proof generated and transaction submitted successfully! (Placeholder)")
            # st.error("Proof verification failed! (Placeholder)")

