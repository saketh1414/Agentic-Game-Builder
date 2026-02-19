// Complete JavaScript
// DOM Element References
const statusDisplay = document.querySelector('.game--status');
const allCells = document.querySelectorAll('.cell');
const newGameButton = document.querySelector('.game--new-game');
const scoreXDisplay = document.querySelector('.score--x');
const scoreODisplay = document.querySelector('.score--o');
const scoreDrawsDisplay = document.querySelector('.score--draws');

// State Variables
let isGameActive = true;
let currentPlayer = 'X';
let gameState = ["", "", "", "", "", "", "", "", ""];
let startingPlayer = 'X';
let score = { X: 0, O: 0, draws: 0 };

// Constants
const winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
];

const winMessage = () => `Player ${currentPlayer} has won!`;
const drawMessage = () => `Game ended in a draw!`;
const currentPlayerTurn = () => `It's ${currentPlayer}'s turn`;

/**
 * Manages a click on a cell.
 * @param {Event} clickedCellEvent - The event object from the click.
 * @returns {void}
 */
function handleCellClick(clickedCellEvent) {
    const clickedCell = clickedCellEvent.target;
    const clickedCellIndex = parseInt(clickedCell.getAttribute('data-cell-index'));

    if (gameState[clickedCellIndex] !== "" || !isGameActive) {
        return;
    }

    handleCellPlayed(clickedCell, clickedCellIndex);
    handleResultValidation();
}

/**
 * Updates the game state and UI for a played cell.
 * @param {HTMLElement} clickedCell - The DOM element of the cell that was clicked.
 * @param {number} clickedCellIndex - The index (0-8) of the cell.
 * @returns {void}
 */
function handleCellPlayed(clickedCell, clickedCellIndex) {
    gameState[clickedCellIndex] = currentPlayer;
    clickedCell.innerText = currentPlayer;
    clickedCell.classList.add(currentPlayer === 'X' ? 'player-x' : 'player-o');
}

/**
 * Switches the current player and updates the status display.
 * @returns {void}
 */
function handlePlayerChange() {
    currentPlayer = currentPlayer === "X" ? "O" : "X";
    statusDisplay.innerText = currentPlayerTurn();
}

/**
 * Checks for win/draw conditions after a move.
 * @returns {void}
 */
function handleResultValidation() {
    let roundWon = false;
    for (let i = 0; i < winningConditions.length; i++) {
        const winCondition = winningConditions[i];
        let a = gameState[winCondition[0]];
        let b = gameState[winCondition[1]];
        let c = gameState[winCondition[2]];
        if (a === '' || b === '' || c === '') {
            continue;
        }
        if (a === b && b === c) {
            roundWon = true;
            break;
        }
    }

    if (roundWon) {
        statusDisplay.innerText = winMessage();
        score[currentPlayer]++;
        updateScoreDisplay();
        isGameActive = false;
        return;
    }

    let roundDraw = !gameState.includes("");
    if (roundDraw) {
        statusDisplay.innerText = drawMessage();
        score.draws++;
        updateScoreDisplay();
        isGameActive = false;
        return;
    }

    handlePlayerChange();
}

/**
 * Resets the board and game state for a new round.
 * @returns {void}
 */
function resetGame() {
    isGameActive = true;
    gameState = ["", "", "", "", "", "", "", "", ""];
    
    // Alternate starting player
    startingPlayer = startingPlayer === 'X' ? 'O' : 'X';
    currentPlayer = startingPlayer;
    
    statusDisplay.innerText = currentPlayerTurn();
    
    allCells.forEach(cell => {
        cell.innerText = "";
        cell.classList.remove('player-x', 'player-o');
    });
}

/**
 * Updates the score display in the DOM.
 * @returns {void}
 */
function updateScoreDisplay() {
    scoreXDisplay.innerText = score.X;
    scoreODisplay.innerText = score.O;
    scoreDrawsDisplay.innerText = score.draws;
}

/**
 * Sets up initial event listeners and UI text.
 * @returns {void}
 */
function initializeGame() {
    statusDisplay.innerText = currentPlayerTurn();
    updateScoreDisplay();

    allCells.forEach(cell => cell.addEventListener('click', handleCellClick));
    newGameButton.addEventListener('click', resetGame);
}

// Start the game
initializeGame();