document.addEventListener('DOMContentLoaded', () => {
    // --- Constants ---
    const CANVAS_WIDTH = 400;
    const CANVAS_HEIGHT = 400;
    const GRID_SIZE = 20;
    const TICK_RATE = 100; // Milliseconds between game ticks (10 ticks/sec)

    const GRID_COUNT_X = CANVAS_WIDTH / GRID_SIZE;
    const GRID_COUNT_Y = CANVAS_HEIGHT / GRID_SIZE;

    const GameState = {
        START_SCREEN: 'START_SCREEN',
        PLAYING: 'PLAYING',
        GAME_OVER: 'GAME_OVER'
    };

    // --- Canvas Setup ---
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;

    // --- Game State Variables ---
    let state = {};
    let lastTickTime = 0;
    let isLoopRunning = false;

    // --- Core Game Functions ---

    /**
     * Resets the game to its initial state for a new game.
     */
    function init() {
        state = {
            snake: [{ x: 10, y: 10 }],
            apple: { x: 15, y: 15 },
            direction: 'RIGHT',
            nextDirection: 'RIGHT',
            score: 0,
            currentState: GameState.PLAYING,
            isWin: false
        };
        generateApple();
    }

    /**
     * The main game loop, driven by requestAnimationFrame.
     * @param {number} currentTime - The current timestamp provided by requestAnimationFrame.
     */
    function gameLoop(currentTime) {
        if (!isLoopRunning) return;

        requestAnimationFrame(gameLoop);

        const elapsed = currentTime - lastTickTime;

        if (elapsed > TICK_RATE) {
            lastTickTime = currentTime;
            if (state.currentState === GameState.PLAYING) {
                update();
            }
        }

        render();

        if (state.currentState === GameState.GAME_OVER) {
            isLoopRunning = false;
        }
    }

    /**
     * Updates the game state for a single tick.
     */
    function update() {
        if (state.currentState !== GameState.PLAYING) return;

        state.direction = state.nextDirection;

        const head = { ...state.snake[0] };
        switch (state.direction) {
            case 'UP': head.y--; break;
            case 'DOWN': head.y++; break;
            case 'LEFT': head.x--; break;
            case 'RIGHT': head.x++; break;
        }

        // Wall Collision Check
        if (head.x < 0 || head.x >= GRID_COUNT_X || head.y < 0 || head.y >= GRID_COUNT_Y) {
            state.currentState = GameState.GAME_OVER;
            return;
        }

        // Self Collision Check
        for (let i = 1; i < state.snake.length; i++) {
            if (head.x === state.snake[i].x && head.y === state.snake[i].y) {
                state.currentState = GameState.GAME_OVER;
                return;
            }
        }

        state.snake.unshift(head);

        // Apple Collision Check
        if (head.x === state.apple.x && head.y === state.apple.y) {
            state.score += 10;
            generateApple();
        } else {
            state.snake.pop();
        }
    }

    /**
     * Renders the entire game state to the canvas.
     */
    function render() {
        // Clear canvas and draw background
        ctx.fillStyle = '#222222';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

        switch (state.currentState) {
            case GameState.START_SCREEN:
                drawText("Snake Game", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 40, 32, 'center');
                drawText("Press Any Key to Start", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, 20, 'center');
                break;

            case GameState.PLAYING:
                // Draw Apple
                drawGridSquare(state.apple.x, state.apple.y, '#FF3333');

                // Draw Snake
                state.snake.forEach((segment, index) => {
                    const color = (index === 0) ? '#33FF33' : '#00CC00';
                    drawGridSquare(segment.x, segment.y, color);
                });

                // Draw Score
                drawText(`Score: ${state.score}`, 10, 25, 20, 'left');
                break;

            case GameState.GAME_OVER:
                const message = state.isWin ? "You Win!" : "Game Over";
                drawText(message, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 40, 32, 'center');
                drawText(`Final Score: ${state.score}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, 20, 'center');
                drawText("Press Any Key to Restart", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 40, 20, 'center');
                break;
        }
    }

    /**
     * Generates a new apple at a random location not occupied by the snake.
     */
    function generateApple() {
        // Check for win condition (snake fills the entire board)
        if (state.snake.length >= GRID_COUNT_X * GRID_COUNT_Y) {
            state.isWin = true;
            state.currentState = GameState.GAME_OVER;
            return;
        }

        let newApplePosition;
        let isOnSnake;
        do {
            isOnSnake = false;
            newApplePosition = {
                x: Math.floor(Math.random() * GRID_COUNT_X),
                y: Math.floor(Math.random() * GRID_COUNT_Y)
            };
            for (const segment of state.snake) {
                if (segment.x === newApplePosition.x && segment.y === newApplePosition.y) {
                    isOnSnake = true;
                    break;
                }
            }
        } while (isOnSnake);

        state.apple = newApplePosition;
    }

    // --- Input Handling ---

    /**
     * Handles keydown events for player controls and game state transitions.
     * @param {KeyboardEvent} event - The keyboard event object.
     */
    function handleKeyPress(event) {
        if (state.currentState === GameState.START_SCREEN || state.currentState === GameState.GAME_OVER) {
            if (!isLoopRunning) {
                isLoopRunning = true;
                init();
                lastTickTime = performance.now();
                requestAnimationFrame(gameLoop);
            }
        } else if (state.currentState === GameState.PLAYING) {
            const key = event.key;
            if (key === 'ArrowUp' && state.direction !== 'DOWN') {
                state.nextDirection = 'UP';
            } else if (key === 'ArrowDown' && state.direction !== 'UP') {
                state.nextDirection = 'DOWN';
            } else if (key === 'ArrowLeft' && state.direction !== 'RIGHT') {
                state.nextDirection = 'LEFT';
            } else if (key === 'ArrowRight' && state.direction !== 'LEFT') {
                state.nextDirection = 'RIGHT';
            }
        }
    }

    // --- Drawing Helper Functions ---

    /**
     * Draws a colored square on the game grid.
     * @param {number} x - The grid x-coordinate.
     * @param {number} y - The grid y-coordinate.
     * @param {string} color - The color of the square.
     */
    function drawGridSquare(x, y, color) {
        ctx.fillStyle = color;
        ctx.fillRect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE);
    }

    /**
     * Draws text on the canvas.
     * @param {string} text - The text to draw.
     * @param {number} x - The x-coordinate.
     * @param {number} y - The y-coordinate.
     * @param {number} size - The font size in pixels.
     * @param {string} align - The text alignment ('center', 'left', 'right').
     */
    function drawText(text, x, y, size, align) {
        ctx.fillStyle = '#FFFFFF';
        ctx.font = `${size}px 'Courier New', monospace`;
        ctx.textAlign = align;
        ctx.fillText(text, x, y);
    }

    // --- Initial Setup ---

    /**
     * Sets up the initial game state and renders the start screen.
     */
    function setup() {
        state.currentState = GameState.START_SCREEN;
        render();
    }

    document.addEventListener('keydown', handleKeyPress);
    setup();
});