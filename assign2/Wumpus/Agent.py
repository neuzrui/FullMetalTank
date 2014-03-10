__author__ = 'Rui Zhang'

import math
from Tkconstants import END
from TheoremProver import TheoremProver

class Agent(object):

    def __init__(self, wumpusWorld, moveHistory, updateCellLabel, updateUI, binPath):
        # components from GUI
        self.wumpusWorld = wumpusWorld
        self.moveHistory = moveHistory
        self.updateCellLabel = updateCellLabel
        self.updateUI = updateUI

        # initialize a knowledge base of the world given
        self.kb = [[''] * wumpusWorld.row for i in range(wumpusWorld.column)]
        # add agent start position information to agent's KB
        agentX, agentY = wumpusWorld.configDict["agent"]
        self.currentPosition = (agentX-1, agentY-1)
        self.kb[agentX-1][agentY-1] = "/A"
        # add goal position information to KB
        goalX, goalY = wumpusWorld.configDict["goal"]
        self.goal =  (goalX-1, goalY-1)
        self.kb[goalX-1][goalY-1] = "/GO"

        # game score, arrow count and step counter
        self.score = 0
        self.arrow = 1
        self.steps = 0

        # the only wumpus is found and its position
        self.wumpusFound = False
        self.wumpusPos = None

        # sets to store different cells
        self.allCells = set([(i,j) for i in range(wumpusWorld.column) for j in range(wumpusWorld.row)])
        self.safeCells = set([])
        self.unknownCells = set([])
        self.dangerousCells = set([])

        # data structure for exploring with DFS
        self.exploringStack = []
        self.explored = set([])
        self.traceStack = []
        self.recheckQueue = []

        # initialize a theorem prover
        self.prover = TheoremProver(self.wumpusWorld.row, self.wumpusWorld.column, binPath)

    def play(self):
        # start position is always safe
        self.safeCells.add(self.currentPosition)
        # use DFS to explore the as large as possible area that the agent can explore
        self.DFSExplore(self.currentPosition)

        # DFS explored all current possible cells
        while len(self.exploringStack) == 0:
            # if the map is completely explored in the first DFS exploration
            if len(self.getUnexploredCells()) == 0:
                self.moveHistory.insert(END, "all cells explored")
                self.moveHistory.see(END)
                self.updateUI(0)
                self.goToGoal()
                break


            # We need to look back at those unknownCells, to see if we can deduce more facts
            self.moveHistory.insert(END, "try to deduce more")
            self.moveHistory.see(END)
            self.updateUI(0)

            self.recheckUnknownCells()
            if len(self.recheckQueue) > 0:
                while len(self.recheckQueue) != 0:
                    nextCell = self.recheckQueue.pop()
                    self.goToCellWithHeuristic(nextCell)
                    # BFS explore on new area
                    self.DFSExplore(self.currentPosition)
                    if len(self.exploringStack) == 0:
                        break
                    self.updateUI(0)

            # cannot deduce more facts at this point
            else:
                self.moveHistory.insert(END, "can't deduce more")
                self.moveHistory.see(END)
                self.updateUI(0)

                # if the exploring queue is empty but the map is not completely explored, there are 2 possibilities:
                # 1. Wumpus is found and it is blocking our way to explore other part of the map
                # 2. The map is unable to be fully explored
                # In case 1, we kill wumpus, then continue exploring
                # In case 2, we go to our goal

                # if already killed wumpus, go to goal
                if self.wumpusFound and self.arrow == 1:
                    cellsNextToWum = self.getAdjacentCells(self.wumpusPos[0], self.wumpusPos[1])
                    unexploredCells = self.getUnexploredCells()
                    unexploredCellNearWum = []
                    for cell in cellsNextToWum:
                        if cell in unexploredCells:
                            unexploredCellNearWum.append(cell)
                    # wumpus is blocking our map, go to kill wumpus and continue explore
                    if unexploredCellNearWum != 0:
                        self.goToKillWumpus(cellsNextToWum)

                    # wumpus is not blocking, go to goal
                    else:
                        self.goToGoal()
                        break
                # no wumpus found so far, can't kill wumpus to explore more cells
                # go to goal directly
                else:
                    self.goToGoal()
                    break


    def DFSExplore(self, startCell):
        self.exploringStack.append(startCell)

        while len(self.exploringStack) != 0:
            nextCell = self.exploringStack.pop()
            # cell is safe to go
            if self.isSafe(nextCell):
                # nextCell is the start point
                if self.currentPosition == nextCell:
                    self.initialStep()
                    continue

                # if the nextCell is not close to current position
                if self.isAdjacentCell(self.currentPosition, nextCell) is False:
                    # find a adjacent cell to nextCell we have explore before and go to that cell
                    previousCell = self.traceStack.pop()
                    while not self.isAdjacentCell(previousCell, nextCell):
                        self.moveToCell(self.currentPosition, previousCell, True)
                        previousCell = self.traceStack.pop()
                    self.moveToCell(self.currentPosition, previousCell, True)

                # current position is at an adjacent cell to nextCell, move forward
                self.moveToCell(self.currentPosition, nextCell)
                self.perceiveCurrentCell(self.currentPosition)
                # get new adjacent cells and store them to exploringStack
                adjacentCells = self.getAdjacentCells(self.currentPosition[0], self.currentPosition[1])
                for cell in adjacentCells:
                    if cell not in self.explored and cell not in self.dangerousCells and cell not in self.exploringStack:
                        self.exploringStack.append(cell)

            else:
                # can't deduce what is the cell
                if nextCell in self.unknownCells:
                    self.moveHistory.insert(END, "unknown at %d,%d" % (nextCell[0]+1, nextCell[1]+1))
                    self.moveHistory.see(END)

            # update the UI to show the current state of game
            self.updateUI(0)


    def initialStep(self):
        self.perceiveCurrentCell(self.currentPosition)
        for cell in self.getAdjacentCells(self.currentPosition[0], self.currentPosition[1]):
            if cell not in self.explored and cell not in self.dangerousCells and cell not in self.exploringStack:
                self.exploringStack.append(cell)




    # return True if cell is safe
    # return False if cell is unknown or dangerous
    # if the cell haven't been checked yet, check it with Prover9
    def isSafe(self, cell):
        # already in sets
        if cell in self.dangerousCells or cell in self.unknownCells:
            return False
        if cell in self.safeCells:
            return True
        return self.checkSafeByProver(cell)


    def checkSafeByProver(self, cell):
        # prove cell to be safe or not
        knowledge = self.generateKnowledge()
        pitTheorem = "Pit(%d,%d).\n" % (cell[0] + 1, cell[1] + 1)
        wumpusTheorem = "Wumpus(%d,%d).\n" % (cell[0] + 1, cell[1] + 1)
        noPitTheorem = "-" + pitTheorem
        noWumpusTheorem = "-" + wumpusTheorem

        # if wumpus is already found in previous steps, only check if there is Pit
        if self.wumpusFound:
            # has no pit proved
            if self.prover.checkTheorem(knowledge, noPitTheorem):
                print "safe cell:", cell
                self.addToSafeCells(cell)
                return True
            # failed to prove there is not pit
            else:
                # has pit proved
                if self.prover.checkTheorem(knowledge, pitTheorem):
                    self.kb[cell[0]][cell[1]] += "/P"
                    self.moveHistory.insert(END, "deduced Pit at %d,%d" % (cell[0]+1, cell[1]+1))
                    self.moveHistory.see(END)
                    self.addToDangerousCells(cell)

                # cannot tell whether there is pit or not
                else:
                    self.unknownCells.add(cell)
                # either dangerous or unknown cell is not safe
                return False

        # wumpus not found yet, check both wumpus and pit
        else:
            # prove there is no pit and wumpus in cell
            noPitProved = self.prover.checkTheorem(knowledge, noPitTheorem)
            noWumpusProved = self.prover.checkTheorem(knowledge, noWumpusTheorem)
            # if there is no pit and wumpus, the cell is safe
            if noPitProved and noWumpusProved:
                # cell is safe, add to queue
                print "safe cell:", cell
                self.addToSafeCells(cell)
                return True

            # if can't prove no pit and no wumpus, cell is not safe
            else:
                if noPitProved is False:
                    pitProved = self.prover.checkTheorem(knowledge, pitTheorem)
                    # if pit in cell, cell is dangerous
                    if pitProved:
                        self.kb[cell[0]][cell[1]] += "/P"
                        self.moveHistory.insert(END, "deduced Pit at %d,%d" % (cell[0]+1, cell[1]+1))
                        self.moveHistory.see(END)
                        self.addToDangerousCells(cell)
                    else:
                        self.unknownCells.add(cell)

                if noWumpusProved is False:
                    wumpusProved = self.prover.checkTheorem(knowledge, wumpusTheorem)
                    # if wumpus in cell, cell is dangerous
                    if wumpusProved:
                        self.kb[cell[0]][cell[1]] += "/W"
                        self.moveHistory.insert(END, "deduced Wum at %d,%d" % (cell[0]+1, cell[1]+1))
                        self.moveHistory.see(END)
                        self.addToDangerousCells(cell)
                        self.wumpusFound = True
                        self.wumpusPos = cell
                    else:
                        self.unknownCells.add(cell)
                return False


    # move from the src cell to target cell. backwards flag indicates whether we are
    # tracing backwards or not
    def moveToCell(self, src, target, backwards=False):
        # if we are going backwards, don't put src in stack
        if not backwards:
            self.traceStack.append(src)

        # remove agent mark from the src cell
        self.wumpusWorld.world[src[0]][src[1]] = self.wumpusWorld.world[src[0]][src[1]].replace("/A","")

        # add agent mark to target and set agent's currentPosition to target
        self.wumpusWorld.world[target[0]][target[1]] += "/A"
        self.moveHistory.insert(END, "move %d,%d" % (target[0]+1, target[1]+1))
        self.moveHistory.see(END)
        self.currentPosition = target

        # deduct 1 score for the move, add one to steps
        self.steps += 1
        self.score -= 1

        # update label in GUI
        self.updateCellLabel(src, target)
        self.updateUI()


    # go to the target cell using Heuristic search, the Heuristic function
    # is the distance between target and current cell
    def goToCellWithHeuristic(self, target):
        while self.currentPosition != target:
            closeCells = self.getAdjacentCells(self.currentPosition[0], self.currentPosition[1])
            hValueDict = {}
            for cell in closeCells:
                if cell in self.safeCells:
                    hValue = self.heuristicValue(cell, target)
                    hValueDict[cell] = hValue
            closestCell = sorted(hValueDict.iteritems(), key=lambda pair: pair[1])[0][0]
            self.moveToCell(self.currentPosition, closestCell)
            self.updateUI(0)


    # check all unknown cells by prover9, deduce more safe cell from them
    def recheckUnknownCells(self):
        cells = list(self.unknownCells)
        for cell in cells:
            if self.checkSafeByProver(cell):
                self.recheckQueue.append(cell)


    # perceive the content in target cell,
    def perceiveCurrentCell(self, cell):
        currentX, currentY = cell[0], cell[1]
        temp = self.wumpusWorld.world[currentX][currentY].replace("/GO","@")

        # gold found! Add points to score
        if temp.find("/G") != -1:
            self.kb[currentX][currentY] += "/G"
            # "dig" the gold, get 1000 points
            self.wumpusWorld.world[currentX][currentY] = temp.replace("/G","").replace("@","/GO")
            self.moveHistory.insert(END, "found gold, + 1000")
            self.moveHistory.see(END)
            self.score += 1000

        if temp.find("/B") != -1:
            # feel breeze, add to knowledge base
            self.kb[currentX][currentY] += "/B"
            self.moveHistory.insert(END, "found breeze")
            self.moveHistory.see(END)

        if temp.find("/S") != -1:
            # feel stench, add to knowledge base
            self.kb[currentX][currentY] += "/S"
            self.moveHistory.insert(END, "found stench")
            self.moveHistory.see(END)

        # add cell to explored set
        self.explored.add(self.currentPosition)
        self.updateUI(0)


    # generate knowledge base for prover9 based on current kb
    def generateKnowledge(self):
        knowledge = ""
        # explored cells in safeCells, generate Breeze and Stench facts
        for x,y in self.safeCells:
            elements = self.kb[x][y].split("/")[1:]
            if "B" in elements:
                knowledge += "Breeze(%d,%d).\n" % (x + 1, y + 1)
            else:
                knowledge += "-Breeze(%d,%d).\n" % (x + 1, y + 1)
            if "S" in elements:
                knowledge += "Stench(%d,%d).\n" % (x + 1, y + 1)
            else:
                knowledge += "-Stench(%d,%d).\n" % (x + 1, y + 1)
        return knowledge


    # get adjacent cells to current cell
    def getAdjacentCells(self, currentX, currentY):
        adjacentCells = []
        # center area
        if currentX != 0 and currentX != self.wumpusWorld.column - 1 \
                and currentY != 0 and currentY != self.wumpusWorld.row - 1:
            adjacentCells.append((currentX, currentY + 1))
            adjacentCells.append((currentX, currentY - 1))
            adjacentCells.append((currentX + 1, currentY))
            adjacentCells.append((currentX - 1, currentY))

        elif currentX == 0:
            # left upper corner case
            if currentY == 0:
                adjacentCells.append((currentX, currentY + 1))
                adjacentCells.append((currentX + 1, currentY))
            # left bottom corner case
            elif currentY == self.wumpusWorld.row - 1:
                adjacentCells.append((currentX, currentY - 1))
                adjacentCells.append((currentX + 1, currentY))
            # left side except corners
            else:
                adjacentCells.append((currentX, currentY + 1))
                adjacentCells.append((currentX, currentY - 1))
                adjacentCells.append((currentX + 1, currentY))

        elif currentX == self.wumpusWorld.column - 1:
            # right upper corner case
            if  currentY == 0:
                adjacentCells.append((currentX, currentY + 1))
                adjacentCells.append((currentX - 1, currentY))
            # right bottom corner case
            elif currentY == self.wumpusWorld.row - 1:
                adjacentCells.append((currentX, currentY - 1))
                adjacentCells.append((currentX - 1, currentY))
            # right side except corners
            else:
                adjacentCells.append((currentX, currentY + 1))
                adjacentCells.append((currentX, currentY - 1))
                adjacentCells.append((currentX - 1, currentY))

        elif currentX != 0 and currentX != self.wumpusWorld.column - 1:
            # top side except corners
            if currentY == 0:
                adjacentCells.append((currentX, currentY + 1))
                adjacentCells.append((currentX + 1, currentY))
                adjacentCells.append((currentX - 1, currentY))
            # bottom side except corners
            elif currentY == self.wumpusWorld.row - 1:
                adjacentCells.append((currentX, currentY - 1))
                adjacentCells.append((currentX + 1, currentY))
                adjacentCells.append((currentX - 1, currentY))

        return adjacentCells


    # getUnexploredCells
    def getUnexploredCells(self):
        return self.allCells.difference(self.explored).difference(self.dangerousCells)


    # go to the goal using Heuristic search
    def goToGoal(self, ):
        print "goToGoal"
        self.moveHistory.insert(END, "go to goal %d,%d" % (self.goal[0], self.goal[1]))
        self.moveHistory.see(END)
        self.updateUI(0)
        self.goToCellWithHeuristic(self.goal)


    # go to the safe close cell to wumpus using Heuristic search and kill wumpus
    def goToKillWumpus(self, cellsNextToWum):
        # find the closest safe cell next to wumpus
        closestSafeCell = None
        minHValue = None
        for cell in cellsNextToWum:
            if cell in self.safeCells:
                hValue = self.heuristicValue(cell, self.currentPosition)
                if minHValue is None:
                    minHValue = hValue
                    closestSafeCell = cell
                else:
                    if hValue < minHValue:
                        minHValue = hValue
                        closestSafeCell = cell
        # move to the safe cell
        self.goToCellWithHeuristic(closestSafeCell)
        # kill wumpus
        wumpusCell = self.wumpusWorld.world[self.wumpusPos[0]][self.wumpusPos[1]]
        self.wumpusWorld.world[self.wumpusPos[0]][self.wumpusPos[1]] = wumpusCell.replace("/W", "")
        self.score -= 100
        self.arrow -= 1
        self.moveHistory.insert(END, "kill wumpus at %d,%d" % (self.wumpusPos[0], self.wumpusPos[1]))
        self.moveHistory.insert(END, "score - 100")
        self.moveHistory.insert(END, "arrow count %d" %  self.arrow)
        self.moveHistory.see(END)
        self.updateUI(0)

        # if the the cell is safe after wumpus is killed
        if self.checkSafeByProver(self.wumpusPos):
            self.addToSafeCells(self.wumpusPos)
            self.moveToCell(self.currentPosition, self.wumpusPos)
            self.DFSExplore(self.currentPosition)
        # otherwise
        else:
            self.moveHistory.insert(END, "wumpus cell not safe")
            self.moveHistory.see(END)
            self.updateUI(0)


    @staticmethod
    def isAdjacentCell(cell1, cell2):
        if abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1]) == 1:
            return True
        else:
            return False


    # adding a cell to safeCells will remove a cell from unknownCells and dangerousCells
    def addToSafeCells(self, cell):
        if cell in self.unknownCells:
            self.unknownCells.remove(cell)
        # will be executed only after we kill the wumpus on cell
        if cell in self.dangerousCells:
            self.dangerousCells.remove(cell)
        self.safeCells.add(cell)


    # adding a cell to dangerousCells will remove a cell from unknownCells
    def addToDangerousCells(self, cell):
        if cell in self.unknownCells:
            self.unknownCells.remove(cell)
        self.dangerousCells.add(cell)


    # heuristicValue is calculated by computing the straight-line
    # distance from cell1 to cell2
    @staticmethod
    def heuristicValue(cell1, cell2):
        return math.pow(cell1[0] - cell2[0],2) + math.pow(cell1[1] - cell2[1],2)














