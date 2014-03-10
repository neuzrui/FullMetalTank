__author__ = 'Rui Zhang'

import time
from WumpusWorld import *
from Tkinter import *
import tkFileDialog, tkFont
from Agent import Agent

class WumpusGUI(Tk):

    counter = 0
    wumpusWorld = None
    agent = None

    canvas_width = 500
    cell_size = 0

    def __init__(self, binPath, mapPath):
        self.binPath = binPath

        Tk.__init__(self)
        self.title("Wumpus 1.0 by Rui Zhang")
        self.font = tkFont.Font(size=12)

        # 4 main frames
        self.worldFrame = LabelFrame(self, width=self.canvas_width, height=self.canvas_width, text="Wumpus World")
        createWorldFrame = LabelFrame(self, text="Create World")
        actionFrame = LabelFrame(self, text="Control Panel")

        self.errorMsgFrame = None
        self.canvas = None
        self.cellLabels = None

        # 3 main frame layout
        self.worldFrame.grid(row=0, column=0, rowspan=2, padx=1, sticky=N+E+W+S)
        createWorldFrame.grid(column=1, row=0, padx=1, sticky=N+E+W+S)
        actionFrame.grid(column=1, row=1, padx=1, sticky=N+E+W+S)

        # worldFrame details
        # place holder for rendering states of the world and error messages
        Frame(self.worldFrame, width=self.canvas_width, height=self.canvas_width).grid(row=0, column=0, sticky=W+E+N+S)

        # createWorld frame details
        Label(createWorldFrame, text="row:").grid(row=0, column=0, sticky=E)
        Label(createWorldFrame, text="column:").grid(row=1, column=0, sticky=E)
        self.rowEntry = Entry(createWorldFrame, width=5)
        self.colEntry = Entry(createWorldFrame, width=5)
        self.rowEntry.grid(row=0, column=1, sticky=W+E)
        self.colEntry.grid(row=1, column=1, sticky=W+E)
        Button(createWorldFrame, text="Load", command=self.loadHandler).grid(row=2, column=0)
        Button(createWorldFrame, text="Generate", command=self.generateWorld).grid(row=2, column=1)

        # actionFrame details
        Button(actionFrame, text="Play", command=self.play).grid(row=0, column=0, sticky=E+W)
        self.moveHistory = Listbox(actionFrame, width=18, height=18)
        self.moveHistory.grid(row=1, column=0, padx=1, pady=1)
        Button(actionFrame, text="Quit", command=self.quit).grid(row=2, column=0, sticky=E+W)

        self.loadWorldFile(mapPath)

    # load world map from given file name path
    def loadWorldFile(self, fileName):
        try:
            if fileName:
                self.wumpusWorld = WumpusWorld(fileName)
                if self.wumpusWorld.initialized:
                    print "initialized"
                    print self.wumpusWorld.world
                    self.cell_size = int(self.canvas_width / (max(self.wumpusWorld.row, self.wumpusWorld.column) + 0.5))
                    self.renderWorld()
                    # pass the functions updateCellLabel and updateUI to agent,
                    #  in order to let the agent control UI
                    self.agent = Agent(self.wumpusWorld, self.moveHistory, self.updateCellLabel,
                                       self.updateUI, self.binPath)
                    self.moveHistory.delete(0, END)
                else:
                    print "Error"
        except ConfigurationError as e:
            message = str(e.value)
            self.showErrorMsg(message)

    # handler for "load" button
    def loadHandler(self):
        # define options for opening or saving a file
        fileOptions = {'defaultextension': '.txt',
                       'initialdir': ".",
                       'filetypes': [('text files', '.txt')],
                       'title': 'Open World Configuration File'}
        fileName = tkFileDialog.askopenfilename(**fileOptions)
        self.loadWorldFile(fileName)

    # let the agent explore the wumpus world automatically
    def play(self):
        if self.agent is None:
            self.showErrorMsg("Please create a world first!")
            return
        self.agent.play()
        self.moveHistory.insert(END, "steps %s" % self.agent.steps)
        self.moveHistory.insert(END, "score %s" % self.agent.score)
        self.moveHistory.see(END)

    # update the cell label after agent's moves
    def updateCellLabel(self, src, target):
        self.cellLabels[src[0]][src[1]].set(self.wumpusWorld.world[src[0]][src[1]])
        self.cellLabels[target[0]][target[1]].set(self.wumpusWorld.world[target[0]][target[1]])

    # update UI to show the most recent state of the world
    def updateUI(self, interval=0.5):
        # set a 0.5s delay in order to let user see the moving process
        time.sleep(interval)
        self.update()

    # render the world on canvas
    def renderWorld(self):
        # clear the message frame before we load the canvas
        if self.errorMsgFrame is not None:
            self.errorMsgFrame.grid_forget()

        # adjust the font size according to the map size,
        # if the row or column becomes bigger, use smaller font size
        if self.wumpusWorld.column > 9 or self.wumpusWorld.row > 9:
            self.font.configure(size=self.font["size"] - 2)

        # initialize the canvas
        self.canvas = Frame(master=self.worldFrame, width=self.canvas_width, height=self.canvas_width)
        self.canvas.grid(row=0, column=0, sticky=N+E+W+S)
        # initialize a two-dimension arrary to store the label we will be showing on the cells
        self.cellLabels = [[''] * self.wumpusWorld.row for i in range(self.wumpusWorld.column)]

        # draw the y\x axis and coordinates
        LabelFrame(self.canvas, height=0.5 * self.cell_size, width=0.5 * self.cell_size, bd=1).grid(row=0, column=0)
        Label(self.canvas, text="y\\x", font=self.font).grid(row=0, column=0)
        for i in range(self.wumpusWorld.column):
            LabelFrame(self.canvas, height=0.5 * self.cell_size, width=self.cell_size, bd=1).grid(row=0, column=i+1)
            Label(self.canvas, text=i+1, font=self.font).grid(row=0, column=i+1)
        for j in range(self.wumpusWorld.row):
                LabelFrame(self.canvas, height=self.cell_size, width=0.5 * self.cell_size, bd=1).grid(row=j+1, column=0)
                Label(self.canvas, text=j+1, font=self.font).grid(row=j+1, column=0)

        # fill in the cells with the information in wumpusWorld.world
        for i in range(self.wumpusWorld.column):
            for j in range(self.wumpusWorld.row):
                labelStr = StringVar()
                labelStr.set(self.wumpusWorld.world[i][j])
                # add the StringVar to the array so that we can update it's value in the whole the game
                self.cellLabels[i][j] = labelStr
                LabelFrame(self.canvas, height=self.cell_size, width=self.cell_size, bd=1).grid(row=j+1, column=i+1)
                Label(self.canvas, textvariable=labelStr, font=self.font).grid(row=j+1, column=i+1)


    # this method is used to show error messages, usually messages are from exceptions thrown
    def showErrorMsg(self, message):
        if self.canvas is not None:
            self.canvas.grid_forget()

        self.errorMsgFrame = Frame(master=self.worldFrame, width=self.canvas_width, height=self.canvas_width)
        self.errorMsgFrame.grid(row=0, column=0, sticky=N+E+W+S)
        Label(self.errorMsgFrame, text=message).grid()


    # generate world according to the dimension specification
    def generateWorld(self):
        # todo: not enough time to work on this part yet
        self.showErrorMsg("Not implemented yet... Please load a file instead")

    # quit game
    def quit(self):
        print "User quit game"
        quit()

if __name__=='__main__':
    if len(sys.argv) != 3:
        print "Usage: python WumpusGUI.py [PROVER9_BINARY_PATH] [MAP_FILE]"
    else:
        wumpus = WumpusGUI(sys.argv[1], sys.argv[2])
        wumpus.mainloop()

