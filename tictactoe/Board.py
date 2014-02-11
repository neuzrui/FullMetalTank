__author__ = 'Ray'


class Board(object):

    emptyCell = ' '
    row = 3
    column = 3

    # To initialize a 3X3 board for the tic tac toe game. We use a two-dimension array to store the
    # marks for player/AI.
    def __init__(self,):
        self.boardGrid = [[self.emptyCell] * self.column for i in range(self.row)]

    # Player/AI use 'O' or 'X', to mark the cells. If other value passed in, raise an exception
    # If the index exceed the boundary, raise exception as well
    def placeMark(self, mark, rowNum, columnNum):
        try:
            if self.cellIsEmpty(rowNum, columnNum) and mark in ["X", "O"]:
                self.boardGrid[rowNum - 1][columnNum - 1] = mark
            else:
                raise MarkError("Error: Cannot place mark %s at the specified position (%s, %s)" % (mark, rowNum, columnNum))
        except IndexError:
            raise IndexError("Error: Position out of boundary")

    # Clear any mark in the cell, which is specified as a cellPosition (rowNum, columnNum)
    def clearMove(self, cellPosition):
        self.boardGrid[cellPosition[0] - 1][cellPosition[1] - 1] = self.emptyCell

    # Check if the specific cell is empty or not.
    # Return True if the cell is empty, otherwise, return False
    def cellIsEmpty(self, rowNum, columnNum):
        if self.boardGrid[rowNum - 1][columnNum - 1] == self.emptyCell:
            return True
        return False

    # Return a list of available moves that a player/AI could place their mark
    # Position is represented by a tuple (rowNum, columnNum)
    def availableMoves(self):
        return [(i + 1, j + 1) for i in range(self.row) for j in range(self.column) if self.cellIsEmpty(i + 1, j + 1)]

    # To test the current state of the board, if there is a winner, return the mark of the winner
    # Otherwise return None
    def terminalTest(self):
        # check horizontal winner
        for i in range(self.row):
            rowList = self.boardGrid[i]
            rowSet = set(rowList)
            if len(rowSet) == 1 and self.emptyCell not in rowSet:
                return rowSet.pop()

        # check vertical winner
        for i in range(self.column):
            columnSet = set()
            for j in range(self.row):
                columnSet.add(self.boardGrid[j][i])
            if len(columnSet) == 1 and self.emptyCell not in columnSet:
                return columnSet.pop()

        # check diagonal winner
        diagonalSet1 = set()
        diagonalSet2 = set()
        for i in range(self.row):
            diagonalSet1.add(self.boardGrid[i][i])
            if i == 0:
                diagonalSet2.add(self.boardGrid[i][2])
            if i == 1:
                diagonalSet2.add(self.boardGrid[i][1])
            if i == 2:
                diagonalSet2.add(self.boardGrid[i][0])
        if len(diagonalSet1) == 1 and self.emptyCell not in diagonalSet1:
            return diagonalSet1.pop()
        elif len(diagonalSet2) == 1 and self.emptyCell not in diagonalSet2:
            return diagonalSet2.pop()

        # no winner at current state
        return None

    # Render the current state of the board on the console according to the dimensions of the board and
    # the current state of boardGrid
    def render(self):
        print "Current state of the board:"
        print "----" * (self.column + 1)
        print "   |", "%d | " * self.column % tuple(i + 1 for i in range(self.column))
        for i in range(self.row):
            print "----" * (self.column + 1)
            print " %d |" % (i + 1),
            print "%s | " * self.column % tuple(self.boardGrid[i][j] for j in range(self.column))
        print "----" * (self.column + 1)

# supporting class for exceptions that may be thrown in method placeMark() of class Board
class MarkError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        repr(self.message)






