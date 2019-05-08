import numpy as np
import random

# Depth of the minimax tree - how many turns the CPU should look ahead before making their move
MAX_DEPTH = 4

# The grid in which the game is played
board = np.array([["*" for col in range(0, 7)] for row in range(0, 6)])
board = np.array([["*", "*", "*", "*", "*", "*", "*"],
                ["*", "*", "*", "*", "*", "*", "*"],
                ["*", "*", "*", "*", "*", "*", "*"],
                ["*", "*", "*", "*", "*", "*", "*"],
                ["*", "*", "*", "*", "*", "*", "*"],
                ["*", "*", "*", "X", "*", "*", "*"]])
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
    return minimaxSearch(board, 0)[0]

# Where the magic happens
def minimaxSearch(board, depth):
    if depth == MAX_DEPTH:
        # print("Depth: 2")
        # print("Score: " + str(heuristic(board)))
        return (-1, heuristic(board))
    # Terminate upon win
    if score(board, "O") >= 10000 or score(board, "X") >= 10000:
        # printBoard(board)
        # print("Depth: " + str(depth))
        
        # # print("Score (X): " + str(score(board, "X")))
        # print("Heuristic: " + str(heuristic(board)))
        # if depth == 1:
        #     print("Score (O): " + str(score(board, "O")))
        #     print("Heuristic: " + str(heuristic(board)))

        # Deducting points for each move rewards wins that occur earlier,
        # even if their heuristic isn't the highest
        return (-1, heuristic(board) - depth * 1000)
    # Loop over each possible move
    best_score = -100000000 # The best hypothetical outcome that any move could produce
    best_move = 0 # The move that produces this best outcome
    for col in range(0, 7):
        if not isColumnFilled(board, col):
            new_board = np.array(board)
            piece = "X" if depth % 2 == 0 else "O"
            placePiece(new_board, col, piece)
            # Odd depths represent the player's turn; they want the heuristic to be as low as possible,
            # so we invert it
            new_score = ((-1) ** depth) * minimaxSearch(new_board, depth + 1)[1]
            # if new_score >= -1000 and depth == 0: 
            #     print(new_score)
            #     print(col)
            # if depth == 0 and col == 0: 
            #     print((-1) ** 1)
            #     print(minimaxSearch(new_board, 1))
            
            # if (depth >= 1):
            #     print("Depth: " + str(depth))
            #     print("Col: " + str(col))
            #     printBoard(new_board)
            #     print("Score: " + str(score(new_board, "X")))
            #     print("Heuristic: " + str(new_score))
            if (new_score > best_score):
                best_score = new_score
                best_move = col
    # Revert the score to its original value
    return (best_move, ((-1) ** depth) * best_score)
    

    # Even depths represent the CPU's turn, so we want the move that leads to the highest heuristic

    # Odd depths represent the player's turn, so we want the move that leads to the lowest heuristic
         


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
def checkWin(board, row, col):
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
            return True
    return False

# Heuristic function representing the CPU's score advantage over the player
def heuristic(board):
    return score(board, "X") - score(board, "O")

# Represents a player's board presence. To calculate the score, we find pairs of pieces sharing a row,
# column, or diagonal, with no opposing pieces in between, and add a subscore based on their distance
def score(board, player):
    score = 0
    # Check rows
    for row in board:
        score += unblocked_pairs(row, player)

    # Check columns
    for col in range(0, 7):
        score += unblocked_pairs(board[:, col], player)

    # Check negative slope diagonals
    # Note: we don't care about diagonals with len < 4!
    # Diagonals constrained by column
    for col in range(1, 4):
        score += unblocked_pairs([board[i - col, i] for i in range(col, 7)], player)
    # Diagonals constrained by row
    for row in range(0, 3):
        score += unblocked_pairs([board[i, i - row] for i in range(row, 6)], player)

    # Check positive slope diagonals
    for col in range(3, 6):
        score += unblocked_pairs([board[col - i, i] for i in range(col, -1, -1)], player)
    for row in range(0, 3):
        score += unblocked_pairs([board[i, 6 - i + row] for i in range(row, 6)], player)
    
    return score

# # The squared sum of the lengths of each continguous chain of pieces owned by a player, representing their
# # board presence
# def score(board, player):
#     score = 0
#     # Check rows
#     for row in board:
#         score += square_sum_chains(row, player)

#     # Check columns
#     for col in range(0, 7):
#         score += square_sum_chains(board[:, col], player)

#     # Check negative slope diagonals
#     # Diagonals constrained by column
#     for col in range(1, 7):
#         score += square_sum_chains([board[i - col, i] for i in range(col, 7)], player)
#     # Diagonals constrained by row
#     for row in range(0, 6):
#         score += square_sum_chains([board[i, i - row] for i in range(row, 6)], player)

#     # Check positive slope diagonals
#     for col in range(0, 6):
#         score += square_sum_chains([board[col - i, i] for i in range(col, -1, -1)], player)
#     for row in range(0, 6):
#         score += square_sum_chains([board[i, 6 - i + row] for i in range(row, 6)], player)
    
#     return score

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
def unblocked_pairs(row, player):
    score = 0
    pieces = [] # Positions of pieces that can form an unblocked pair with the current index
    for col, val in enumerate(row):
        if val == player:
            # Check win condition
            if len(pieces) == 3 and col - pieces[0] == 3:
                return 10000
            for old_col in pieces:
                dist = col - old_col
                score += (7 - dist) ** 2
            pieces.append(col)
        elif val == "*":
            pass
        else:
            # Hit a block
            pieces.clear()
    return score



# Utility squared sum function
def square_sum_chains(row, player):
    score = 0
    # The index at which the current chain begins
    start_index = 0
    for index, value in enumerate(row):
        if value == player:
            # Detect beginning of chain
            if index == 0 or row[index-1] != player:
                start_index = index
            # Detect end of row
            if index == len(row) - 1:
                length = index - start_index + 1
                score += length ** 3
                if (length >= 4): score += 10000 # Heuristic heavily favors wins
        if value != player:
            # Detect end of chain
            if index > 0 and row[index-1] == player:
                length = index - start_index
                score += length ** 3
                if (length >= 4): score += 10000

    return score

while True:
    printBoard(board)
    print("Score (O): " + str(score(board, "O")))
    print("Score (X): " + str(score(board, "X")))
    col = playerTurn()
    row, col = placePiece(board, col, "O")
    
    if checkWin(board, row, col):
        printBoard(board)
        print("O wins!")
        quit()
    
    col = cpuTurn()
    # col = random.randint(0, 6)
    # while isColumnFilled(board, col): col = random.randint(0, 6)
    row, col = placePiece(board, col, "X")
    if checkWin(board, row, col):
        printBoard(board)
        print("X wins!")
        quit()