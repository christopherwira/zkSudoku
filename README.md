# Privacy-Preserving Sudoku Race

This is a project for a university workshop demonstrating how to build a privacy-preserving DApp using Zero-Knowledge Proofs. The application allows users to prove they have solved a Sudoku puzzle to win a prize from a smart contract, without revealing their solution.

## Core Technologies

- **Blockchain:** Hardhat (local Ethereum node)
- **Zero-Knowledge Proofs:** ZoKrates
- **Smart Contracts:** Solidity
- **Backend/UI:** Python with Streamlit
- **Environment:** Docker & VS Code Dev Containers

---

## Getting Started

This project is configured to run in a VS Code Dev Container, which creates a consistent and reproducible development environment.

### Prerequisites

1.  **Git:** [Download & Install Git](https://git-scm.com/downloads)
2.  **Docker Desktop:** [Download & Install Docker](https://www.docker.com/products/docker-desktop/)
3.  **VS Code:** [Download & Install VS Code](https://code.visualstudio.com/)
4.  **VS Code Dev Containers Extension:** Install this from the VS Code Marketplace.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/zkSudoku.git](https://github.com/your-username/zkSudoku.git)
    ```

2.  **Open the project in VS Code:**
    ```bash
    cd zkSudoku
    code .
    ```

3.  **Reopen in Container:**
    A notification will appear at the bottom-right corner asking you to "Reopen in Container". Click it.

    VS Code will now build the Docker containers and set up the entire development environment for you. This may take a few minutes on the first run.

4.  **Run the Application:**
    Once the container is built and you are inside the dev environment, open a new terminal in VS Code (`Ctrl+Shift+\``) and run the application:
    ```bash
    docker-compose up
    ```
    You can then access the Streamlit web app at **http://localhost:8501**.