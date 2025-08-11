// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./generated/ZksudokuVerifier.sol";

contract Zksudoku is Verifier {
    // --- State Variables ---

    // The Sudoku problem that are tied to this smart contract
    uint[81] public sudoku_problem;

    // The prize amount for each winner (e.g., 10 ETH).
    uint256 public constant PRIZE_AMOUNT = 10 ether;

    // The total number of winners allowed.
    uint256 public constant MAX_WINNERS = 3;

    // An array to store the addresses of the winners.
    address[MAX_WINNERS] public winners;

    // A counter for the number of winners so far.
    uint8 public winnerCount;

    // A mapping to efficiently check if an address has already won.
    mapping(address => bool) public hasWon;

    // --- Events ---
    event NewWinner(address indexed winner, uint256 prize);

    /**
     * @dev The constructor is payable to receive the initial prize pool funding.
     * The deployer must send at least `PRIZE_AMOUNT * MAX_WINNERS` ETH upon deployment.
     */
    constructor(uint[81] memory _sudoku_problem) payable {
        require(
            msg.value >= PRIZE_AMOUNT * MAX_WINNERS,
            "Must fund the contract with enough ETH for all prizes"
        );
        sudoku_problem = _sudoku_problem;
    }

    function getSudokuProblem() public view returns (uint256[81] memory) {
        return sudoku_problem;
    }

    function getWinners() public view returns (address[MAX_WINNERS] memory) {
        return winners;
    }

    /**
     * @notice Allows a user to submit a ZK-SNARK proof to claim a prize.
     * @param proof The proof is a struct containing 2 G1 and 1 G2 points.
     * @param input The public inputs for the proof (in this case, the board hash).
     */
    function submitSolution(
        Proof memory proof, 
        uint[81] memory input
    ) public {
        // --- Pre-flight Checks ---
        require(winnerCount < MAX_WINNERS, "The race is already over");
        require(!hasWon[msg.sender], "You have already won a prize");

        // --- Proof Verification ---
        // Check that the proof public input is the same as our proposed problem
        // Call the verifyTx function inherited from ZksudokuVerifier.
        // This is the core of the privacy-preserving logic.
        require(_compareBoards(sudoku_problem, input), "The provided input instance is not valid");
        bool proofIsValid = verifyTx(proof, input);
        require(proofIsValid, "The provided proof is not valid");

        // --- State Updates & Prize Distribution ---
        hasWon[msg.sender] = true;
        winners[winnerCount] = msg.sender;
        winnerCount++;

        // Transfer the prize money to the winner.
        (bool sent, ) = msg.sender.call{value: PRIZE_AMOUNT}("");
        require(sent, "Failed to send prize ETH");

        // Emit an event to log the new winner.
        emit NewWinner(msg.sender, PRIZE_AMOUNT);
    }

    /**
     * @notice A helper function to check the remaining balance of the contract.
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function _compareBoards(uint256[81] memory _sudoku_problem, uint256[81] memory _input) internal pure returns (bool) {
        for (uint i = 0; i < 81; i++) {
            if (_sudoku_problem[i] != _input[i]) {
                return false;
            }
        }
        return true;
    }
}
