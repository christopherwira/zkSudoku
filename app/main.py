import streamlit as st
import pandas as pd
import numpy as np
from typing import List

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

# --- Helper Functions & Styling ---

def get_solution_grid() -> List[List[int]]:
    """
    Retrieves the current state of the user's solution from Streamlit's session state.
    Initializes it if it doesn't exist.
    """
    if 'solution_grid' not in st.session_state:
        # Initialize the solution grid as a copy of the problem
        st.session_state.solution_grid = [row[:] for row in SUDOKU_PROBLEM]
    return st.session_state.solution_grid

def update_cell(row: int, col: int, value: str):
    """Updates a single cell in the session state's solution grid."""
    try:
        # Convert input to integer, handle empty string as 0
        num_value = int(value) if value else 0
        if 0 <= num_value <= 9:
            st.session_state.solution_grid[row][col] = num_value
        else:
            st.warning("Please enter a number between 1 and 9.")
    except ValueError:
        st.warning("Invalid input. Please enter a number.")

def style_sudoku_grid(df: pd.DataFrame):
    """Applies styling to the Sudoku grid for better visualization."""
    
    def cell_style(val, row_idx, col_idx):
        """Determines the CSS style for a single cell based on its value and position."""
        is_clue = SUDOKU_PROBLEM[row_idx][col_idx] != 0
        
        style = 'color: #1E293B; background-color: #F8FAFC;' # Default for user input
        if is_clue:
            style = 'color: #475569; background-color: #E2E8F0; font-weight: bold;' # Style for clues
        
        # Add thicker borders for 3x3 subgrids
        if (row_idx + 1) % 3 == 0 and row_idx != 8:
            style += ' border-bottom: 2px solid #94A3B8;'
        if (col_idx + 1) % 3 == 0 and col_idx != 8:
            style += ' border-right: 2px solid #94A3B8;'
            
        return style

    def apply_styles(df_to_style):
        """Applies the cell_style function to the entire DataFrame."""
        styler_df = pd.DataFrame('', index=df_to_style.index, columns=df_to_style.columns)
        for r_idx, row in enumerate(df_to_style.itertuples(index=False)):
            for c_idx, val in enumerate(row):
                styler_df.iloc[r_idx, c_idx] = cell_style(val, r_idx, c_idx)
        return styler_df

    # --- THE FIX ---
    # Use the Styler's `format` method to display 0s as empty strings,
    # without changing the underlying integer data. Then, apply the styles.
    return df.style.format(lambda val: '' if val == 0 else val).apply(apply_styles, axis=None)

# --- Main Application UI ---

st.title("🧩 ZK-Sudoku Race")
st.markdown("Prove you've solved the Sudoku to win a prize from the smart contract!")

# --- Main Layout ---
col1, col2 = st.columns([2, 1]) # Create a 2/3 and 1/3 column layout

with col1:
    st.header("The Puzzle")
    
    # Create a container for the grid
    grid_container = st.container()

    # Display the Sudoku grid using a DataFrame for easy styling
    solution = get_solution_grid()
    # Keep the DataFrame with integer types (0 for empty)
    df = pd.DataFrame(solution)
    
    # Apply custom styling to the DataFrame
    styled_grid = style_sudoku_grid(df)
    grid_container.dataframe(styled_grid, use_container_width=True, height=500)

with col2:
    st.header("Your Move")

    # --- User Input Section ---
    with st.form("input_form"):
        st.write("Enter a number (1-9) into an empty cell.")
        
        # Use Streamlit's columns for a neat layout
        input_col1, input_col2, input_col3 = st.columns(3)
        
        with input_col1:
            row = st.number_input("Row", min_value=1, max_value=9, step=1)
        with input_col2:
            col = st.number_input("Column", min_value=1, max_value=9, step=1)
        with input_col3:
            val = st.text_input("Value", max_chars=1)

        update_button = st.form_submit_button("Update Cell")

        if update_button:
            # Adjust for 0-based indexing
            row_idx, col_idx = row - 1, col - 1
            if SUDOKU_PROBLEM[row_idx][col_idx] == 0:
                update_cell(row_idx, col_idx, val)
                st.rerun() # Rerun the script to update the displayed grid
            else:
                st.error("This cell is a clue and cannot be changed.")

    st.divider()

    # --- Submission Section ---
    st.subheader("Submit Your Solution")
    if st.button("Generate Proof & Submit to Contract", type="primary"):
        solution_grid = get_solution_grid()
        
        st.write("Current Solution Grid:")
        st.json(solution_grid)
        
        with st.spinner("Generating proof... this may take a moment."):
            print(solution_grid)
            # --- TODO: INTEGRATION POINT ---
            # 1. Call your zokrates_utils to generate the proof using the `solution_grid`.
            # 2. Call your web3_utils to parse the proof and call the smart contract.
            # 3. Handle the success or failure response.
            st.success("Proof generated and transaction submitted successfully! (Placeholder)")
            # st.error("Proof verification failed! (Placeholder)")
