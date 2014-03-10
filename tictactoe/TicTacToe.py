__author__ = 'Rui Zhang'

import random
from Player import *
from Board import *


class TicTacToe(object):

    # Output prompts to let the user choose mark and decide which player go first
    def run(self):
        print "\nWelcome to TicTacToe game!"
        userInput = raw_input("Choose your mark, 'X' or 'O'? Enter 'Q' to exit.\n").upper()
        if userInput in ["X", "O"]:
            self.player = Player(userInput)
            if userInput == "X":
                self.ai = AIPlayer("O")
            else:
                self.ai = AIPlayer("X")
            print "Your mark is '%s' and the AI player's mark is '%s'" % (self.player.mark, self.ai.mark)
            board = Board()
            board.render()

            # player and AI have the same probability to go first
            if random.random() >= 0.5:
                print "You are lucky, you go first"
                self.play(board, self.player)
            else:
                print "Sorry, AI go first"
                self.play(board, self.ai)

            return True
        # user quit the game
        elif userInput == "Q":
            print "Quit game"
            return False
        # user input invalid character
        else:
            print "Invalid choice!"
            return True

    def play(self, board, startPlayer):

        # if AI go first, choose a random cell to mark
        if startPlayer.mark == self.ai.mark:
            randomCell = (random.randint(1, 3), random.randint(1, 3))
            print "AI placed its mark randomly at", randomCell
            self.ai.markCell(board, randomCell[0], randomCell[1])
            board.render()

        # user put their marks and AI play against user after user placing his mark
        while True:
            userInput = raw_input("Enter the cell position to be marked (example '1 1' means row1, column1)\n")
            if self.validPosition(userInput, board):
                rowNum = int(userInput.split()[0])
                columnNum = int(userInput.split()[1])
                # player put his mark
                self.player.markCell(board, rowNum, columnNum)
                print "You placed your mark at", (rowNum, columnNum)
                board.render()
                if self.isFinished(board):
                    break

                # AI's turn
                self.ai.evaluateAndMarkCell(board)
                board.render()
                if self.isFinished(board):
                    break

            else:
                print "Invalid position, please enter a new position\n"
        del board

    # Check if the game reaches its final state,
    # If yes, output who is the winner before return True
    # Otherwise, return False to indicate the game should keep going
    def isFinished(self, board):
        winner = board.terminalTest()
        # actual winner found
        if winner is not None:
            if winner == self.player.mark:
                print "Congratulations! You win the game!"
                return True
            else:
                print "AI win the game! Sorry!"
                return True
        # player and AI are draw
        if len(board.availableMoves()) == 0:
            print "You and AI are draw, no winner this time!"
            return True

        return False

    # Check if the user input a valid position on the board
    def validPosition(self, userInput, board):
        coordinates = userInput.split()
        if len(coordinates) == 2 and coordinates[0].isdigit() and coordinates[1].isdigit():
            rowNum = int(coordinates[0])
            columnNum = int(coordinates[1])
            # given position of the cell is filled with mark
            if 1 <= rowNum <= board.row and 1 <= columnNum <= board.column:
                return board.cellIsEmpty(rowNum, columnNum)
            # given position out of boundary
            else:
                return False
        else:
            return False

# main function of the TicTacToe game
if __name__ == "__main__":
    ticTacToe = TicTacToe()
    flag = True
    while flag:
        flag = ticTacToe.run()



