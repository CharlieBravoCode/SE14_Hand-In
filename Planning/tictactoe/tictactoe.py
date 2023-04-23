"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Set initial counts
    x_count = 0
    o_count = 0

    # Count number of Xs and Os
    for row in board:
        for cell in row:
            if cell == X:
                x_count += 1
            elif cell == O:
                o_count += 1

    return O if x_count > o_count else X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Initialize set of possible actions
    possible_actions = set()

    # Add all empty cells to the set of possible actions
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Check if action is valid
    if action not in actions(board):
        raise ValueError("Invalid action")

    # Create a copy of the board and make the move
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check if there is a winner
    for player in [X, O]:

        # Check rows
        for row in board:
            if all(cell == player for cell in row):
                return player

        # Check columns
        for col in range(3):
            if all(board[row][col] == player for row in range(3)):
                return player

        # Check diagonals
        if all(board[i][i] == player for i in range(3)):
            return player

        # Check other diagonal
        if all(board[i][2 - i] == player for i in range(3)):
            return player

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # Terminal state if there is a winner or all cells are filled
    return winner(board) is not None or all(board[i][j] != EMPTY for i in range(3) for j in range(3))


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    # Check if there is a winner
    winner_player = winner(board)

    if winner_player == X:
        return 1
    elif winner_player == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # Minimax algorithm (max player)
    def max_value(state, alpha, beta):

        # Check if state is terminal
        if terminal(state):
            return utility(state), None

        # Initialize value and optimal action
        value = -math.inf
        optimal_action = None

        # Find optimal action
        for action in actions(state):
            new_value, _ = min_value(result(state, action), alpha, beta)
            if new_value > value:
                value = new_value
                optimal_action = action
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return value, optimal_action

    # Minimax algorithm (min player)
    def min_value(state, alpha, beta):

        # Check if state is terminal
        if terminal(state):
            return utility(state), None

        # Initialize value and optimal action
        value = math.inf
        optimal_action = None

        # Find optimal action for min player
        for action in actions(state):
            new_value, _ = max_value(result(state, action), alpha, beta)
            if new_value < value:
                value = new_value
                optimal_action = action
            beta = min(beta, value)
            if alpha >= beta:
                break

        return value, optimal_action

    # Check if board is terminal
    if terminal(board):
        return None

    # Find optimal action for current player
    current_player = player(board)
    if current_player == X:
        _, optimal_action = max_value(board, -math.inf, math.inf)
    else:
        _, optimal_action = min_value(board, -math.inf, math.inf)

    return optimal_action


