"""
Tic Tac Toe Player
"""

import math

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
    # Count number of X's and O's
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    
    # X goes first, so if counts are equal, it's X's turn
    # If X has one more move than O, it's O's turn
    return X if x_count == o_count else O
 

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    
    # Check each cell in the board
    for i in range(3):
        for j in range(3):
            # If cell is empty, it's a possible action
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
    
    # Create a deep copy of the board
    new_board = [row[:] for row in board]
    
    # Get current player
    current_player = player(board)
    
    # Make the move
    i, j = action
    new_board[i][j] = current_player
    
    return new_board
  

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if row.count(row[0]) == 3 and row[0] != EMPTY:
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    
    # No winner
    return None
 


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    # Check if all cells are filled (draw)
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Get winner
    game_winner = winner(board)
    
    # Return appropriate value based on winner
    if game_winner == X:
        return 1
    elif game_winner == O:
        return -1
    else:
        return 0



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Return None if game is over
    if terminal(board):
        return None
    
    current_player = player(board)
    
    def max_value(board, alpha=-math.inf, beta=math.inf):
        if terminal(board):
            return utility(board), None
        v = -math.inf
        best_action = None
        for action in actions(board):
            min_val, _ = min_value(result(board, action), alpha, beta)
            if min_val > v:
                v = min_val
                best_action = action
            alpha = max(alpha, v)
            if alpha >= beta:
                break
        return v, best_action
    
    def min_value(board, alpha=-math.inf, beta=math.inf):
        if terminal(board):
            return utility(board), None
        v = math.inf
        best_action = None
        for action in actions(board):
            max_val, _ = max_value(result(board, action), alpha, beta)
            if max_val < v:
                v = max_val
                best_action = action
            beta = min(beta, v)
            if alpha >= beta:
                break
        return v, best_action
    
    # Choose max or min value based on current player
    if current_player == X:
        _, action = max_value(board)
    else:
        _, action = min_value(board)
    
    return action

