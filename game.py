import numpy as np
import random

# Depth of the minimax tree - how many turns the CPU should look ahead before making their move
MAX_DEPTH = 6

# The grid in which the game is played
board = np.array([["*" for col in range(0, 7)] for row in range(0, 6)])
board = np.array([["X", "*", "O", "X", "X", "*", "X"],
                ["O", "*", "X", "O", "X", "*", "O"],
                ["X", "*", "X", "X", "X", "*", "O"],
                ["O", "*", "X", "O", "O", "*", "X"],
                ["O", "O", "O", "X", "X", "O", "O"],
                ["X", "O", "X", "O", "O", "X", "O"]])

# Sequence of move for debugging purposes
seq = []
# Receive/validate player input
def playerTurn():

    col = input("Select a column to place your piece in (1-7): ")
    
    try:
        # Convert to 0-index
        col = int(col) - 1
    except ValueError:
        print("Input must be a single integer!")
        return playerTurn()
    if col < 0 or col > 6:
        print("Column must be between 1 and 7!")
        return playerTurn()
    if isColumnFilled(board, col):
        print("The col you chose is full!")
        return playerTurn()
    return col

# Initiate the minimax algorithm and return its result
def cpuTurn():
    return minimaxSearch(board, 0, None)

# Where the magic happens
def minimaxSearch(board, depth, alpha):
    if depth == MAX_DEPTH:
        return heuristic(board)
    # Terminate upon win
    if score(board, "O") >= 10000 or score(board, "X") >= 10000:
        return heuristic(board) - depth * 1000
    # Loop over each possible move
    best_score = None # The max or min heuristic that any move could produce
    best_move = 0 # The move that produces this best outcome
    for col in range(0, 7):
        if not isColumnFilled(board, col):
            new_board = np.array(board)
            piece = "X" if depth % 2 == 0 else "O"
            placePiece(new_board, col, piece)
            # Odd depths represent the player's turn; they want the heuristic to be as low as possible,
            # so we invert it
            new_score = minimaxSearch(new_board, depth + 1, best_score)
            # Just assign the first value as the best, nothing to compare it to
            if best_score is None: 
                best_score = new_score
                best_move = col
            if depth % 2 == 0: # Maximizing player's turn (X)
                if new_score > best_score:
                    best_score = new_score
                    best_move = col
                    if alpha is not None and best_score > alpha:
                        # Alpha-beta prune this branch
                        return best_score
            else:
                if new_score < best_score:
                    best_score = new_score
                    best_move = col
                    if alpha is not None and best_score < alpha:
                        # Alpha-beta prune this branch
                        return best_score
                 # Minimizing player's turn (O)
                
    # Return the heuristic score if not the ground state, otherwise return the move the CPU will play
    return best_score if depth > 0 else best_move

# Update the board with the new piece's position and return this position
# The value of team is 0 for player, 1 for CPU
def placePiece(board, col, piece):
    row = 5
    while board[row][col] != "*":
        row -= 1
    board[row][col] = piece
    return (row, col)

# Each piece is part of a contiguous chain of pieces that spans four directions: horizontal,
# vertical, positive slope diagonal, and negative slope diagonal. Take the following example:
# * * * * * * * *
# * * * * * * * *
# * * * * * x * *
# x * * * x * * *
# * x * x * * * *
# * x X * * * * *
# The capital X's horizontal chain is length 2; its vertical chain is length 1; its positive chain is
# length 4; and its negative chain is length 3. We know that if victory is achieved, it must have
# been achieved using the most recent piece. Thus we search for a chain from this piece at least 4 long.
def checkWin(board, row, col, player):
    piece = board[row][col]
    if piece == "*": return False # Shouldn't happen but just as a precaution

    # Lengths of the horizontal, vertical, positive, and negative sloped chains, in that order
    lengths = [1, 1, 1, 1]

    # Represent movement along horizontal, vertical pos, and neg chains
    directions = [[0, 1], [1, 0], [-1, 1], [-1, -1]]

    for index, direction in enumerate(directions):
        # Reverse direction first
        searchRow = row - direction[0]
        searchCol = col - direction[1]
        while inBounds(searchRow, searchCol) and board[searchRow][searchCol] == piece:
            lengths[index] += 1
            searchRow -= direction[0]
            searchCol -= direction[1]
        # Positive direction
        searchRow = row + direction[0]
        searchCol = col + direction[1]
        while inBounds(searchRow, searchCol) and board[searchRow][searchCol] == piece:
            lengths[index] += 1
            searchRow += direction[0]
            searchCol += direction[1]

    for length in lengths:
        if length >= 4: 
            printBoard(board)
            print(player + " wins!")
            save_moves = input("Would you like to save the sequence of moves? (Y/N) ")
            if save_moves == "Y":
                [print(col+1) for col in seq]
            quit()

# Heuristic function representing the CPU's score advantage over the player
def heuristic(board):
    return score(board, "X") - score(board, "O")

# Represents a player's board presence. To calculate the score, we search for chains of 4 cells along
# every row, column, or diagonal with no opposing pieces in them, and add the square of the number of
# player pieces in that chain to the score
def score(board, player):
    score = 0
    # Check rows
    for row in board:
        score += subscore(row, player)

    # Check columns
    for col in range(0, 7):
        score += subscore(board[:, col], player)

    # Check negative slope diagonals
    # Note: we don't care about diagonals with len < 4!
    # Diagonals constrained by column
    for col in range(1, 4):
        score += subscore([board[i - col, i] for i in range(col, 7)], player)
    # Diagonals constrained by row
    for row in range(0, 3):
        score += subscore([board[i, i - row] for i in range(row, 6)], player)

    # Check positive slope diagonals
    for col in range(3, 6):
        score += subscore([board[col - i, i] for i in range(col, -1, -1)], player)
    for row in range(0, 3):
        score += subscore([board[i, 6 - i + row] for i in range(row, 6)], player)
    return score

# Display the board with pretty formatting
def printBoard(board):
    print ("  1 2 3 4 5 6 7")
    for index, row in enumerate(board):
        print(str(index+1) + " " + " ".join(row))
    # print("o" + str(score(board, "O")))
    # print("x" + str(score(board, "X")))

def isColumnFilled(board, col):
    return board[0][col] != "*"

# Utility bounds-checking function
def inBounds(row, col):
    return row >= 0 and col >= 0 and row < 6 and col < 7

# Utility scoring function for a single row/column/diagonal
def subscore(row, player):
    # print(row)
    score = 0

    for start in range(0, len(row) - 3):
        num_players = 0 # Reset so it doesn't count for points
        for col in range(start, start + 4):
            val = row[col]
            if val == player:
                num_players += 1
            elif val != "*":
                # If there are opponent pieces in this block, you can't produce a connect 4 with it
                num_players = 0 # Reset so it doesn't count for points
                break 
        if num_players == 4: # Check win condition
            return 10000
        else:
            score += num_players ** 2
        
    # print(score)
    return score

while True:
    printBoard(board)
    print("Score (O): " + str(score(board, "O")))
    print("Score (X): " + str(score(board, "X")))
    col = playerTurn()
    row, col = placePiece(board, col, "O")
    seq.append(col)
    
    checkWin(board, row, col, "O")

    col = cpuTurn()
    # col = random.randint(0, 6)
    # while isColumnFilled(board, col): col = random.randint(0, 6)
    row, col = placePiece(board, col, "X")
    seq.append(col)
    checkWin(board, row, col, "X")