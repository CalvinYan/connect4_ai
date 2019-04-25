import numpy as np
import random

# The grid in which the game is played
board = [["*" for col in range(0, 7)] for row in range(0, 6)]
# Receive/validate player input
def playerTurn():
    global board

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
    if board[0][col] != "*":
        print("The col you chose is full!")
        return playerTurn()
    return col

# Update the board with the new piece's position and return this position
# The value of team is 0 for player, 1 for CPU
def placePiece(col, piece):
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
def checkWin(row, col):
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
        # print(length)
        if length >= 4: 
            return True
    return False

# Display the board with pretty formatting
def printBoard():
    print ("1 2 3 4 5 6 7")
    for row in board:
        print(" ".join(row))

# Utility bounds-checking
def inBounds(row, col):
    return row >= 0 and col >= 0 and row < 6 and col < 7

while True:
    col = playerTurn()
    row, col = placePiece(col, "O")
    
    if checkWin(row, col):
        printBoard()
        print("O wins!")
        quit()
    
    col = random.randint(0, 6)
    while board[0][col] != "*": col = random.randint(0, 6)
    row, col = placePiece(col, "X")
    printBoard()
    if checkWin(row, col):
        print("X wins!")
        quit()


