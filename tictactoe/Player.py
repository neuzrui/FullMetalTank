__author__ = 'Rui Zhang'

# Human player and AI player are all Player. However, human player should only have mark(...) to mark the cell on board,
# AI player should use evaluateAndMark(...) to mark the cell. evaluateAndMark(...) will call minimaxDecision()
# to find out the best move to win the game or prevent the human player winning.
class Player():
    def __init__(self, mark):
        self.mark = mark
        marks = ["X", "O"]
        marks.remove(self.mark)
        self.opponentMark = marks.pop()

    # this method is for human player to mark the wanted cell, decision is made by human
    def markCell(self, board, rowNum, columnNum):
        board.placeMark(self.mark, rowNum, columnNum)

# AI player extends the basic player
class AIPlayer(Player):

    # large enough number to be used as infinity
    infinity = 1000000

    # this method is for human player to mark the wanted cell, decision is made by human
    def evaluateAndMarkCell(self, board):
        # use minimax algorithm to get the best next move
        bestMove = self.minimaxDecision(board)
        print "AI placed its mark at", bestMove
        # execute the best move
        self.markCell(board, bestMove[0], bestMove[1])

    # evaluate all moves possible and get their min value. Then find the best move among those moves
    def minimaxDecision(self, board):
        availableMoves = board.availableMoves()
        strategies = []
        # get all minValues result from availableMoves
        for move in availableMoves:
            value = self.minValue(self.result(board, move, self.mark))
            board.clearMove(move)
            strategies.append((move, value))
        strategies.sort(key=lambda strategy: strategy[1], reverse = True)
        # return the first one of those optimal moves
        return strategies[0][0]

    # Calculate minimized Max value
    def minValue(self, board):
        # Check if the given state is a final state, if it is, return the utility of the final state
        winner = board.terminalTest()
        if winner is not None:
            if winner == self.mark:
                return 1
            else:
                return -1
        if winner is None and len(board.availableMoves()) == 0:
            return 0

        # if the given state is not a final state,
        # keep searching the it subtrees to get the best Max value of current state
        value = self.infinity
        for move in board.availableMoves():
            value = min(value, self.maxValue(self.result(board, move, self.opponentMark)))
            board.clearMove(move)
        return value

    # Calculate maximized Min value
    def maxValue(self, board):
        # Check if the given state is a final state, if it is, return the utility of the final state
        winner = board.terminalTest()
        if winner is not None:
            if winner == self.mark:
                return 1
            else:
                return -1
        if winner is None and len(board.availableMoves()) == 0:
            return 0

        # if the given state is not a final state,
        # keep searching the it subtrees to get the best Min value of current state
        value = -self.infinity
        for move in board.availableMoves():
            value = max(value, self.minValue(self.result(board, move, self.mark)))
            board.clearMove(move)
        return value

    # execute move and return the result state after the move
    def result(self, board, move, mark):
        board.placeMark(mark, move[0], move[1])
        return board




