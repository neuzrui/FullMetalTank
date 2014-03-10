__author__ = 'Rui Zhang'

class WumpusWorld(object):

    def __init__(self, confFileName):
        self.world = None
        self.initialized = False
        self.column = 0
        self.row = 0
        self.configDict = None
        try:
            # get the configurations from the given file
            configLines = file(confFileName, "r").readlines()

            if configLines is not []:
                self.configDict = {"mapSize": None, "agent": None,  "goal": None, "wumpus": None,
                              "breeze": [], "gold": [], "pit": [], "stench": []}

                # collect world configuration into the configDict
                for line in configLines:
                    if line.startswith("M"):
                        column, row = self.extractPosition(line, "M")
                        if self.configDict["mapSize"] is None:
                            self.configDict["mapSize"] = column, row
                        else:
                            raise ConfigurationError("More than one map size configuration found")

                    elif line.startswith("A"):
                        posX, posY = self.extractPosition(line, "A")
                        if self.configDict["agent"] is None:
                            self.configDict["agent"] = posX, posY
                        else:
                            raise ConfigurationError("More than one agent configuration found")

                    elif line.startswith("GO"):
                        posX, posY = self.extractPosition(line, "GO")
                        if self.configDict["goal"] is None:
                            self.configDict["goal"] = posX, posY
                        else:
                            raise ConfigurationError("More than one goal configuration found")

                    elif line.startswith("W"):
                        posX, posY = self.extractPosition(line, "W")
                        if self.configDict["wumpus"] is None:
                            self.configDict["wumpus"] = posX, posY
                        else:
                            raise ConfigurationError("More than one wumpus configuration found")

                    elif line.startswith("B"):
                        posX, posY = self.extractPosition(line, "B")
                        self.configDict["breeze"].append((posX,posY))

                    elif line.startswith("G"):
                        posX, posY = self.extractPosition(line, "G")
                        self.configDict["gold"].append((posX,posY))

                    elif line.startswith("P"):
                        posX, posY = self.extractPosition(line, "P")
                        self.configDict["pit"].append((posX,posY))

                    elif line.startswith("S"):
                        posX, posY = self.extractPosition(line, "S")
                        self.configDict["stench"].append((posX,posY))

                    # invalid configuration found
                    else:
                        raise ConfigurationError("Invalid configuration %s found" % line)

                # everything is collected to initialize the world
                self.__initializeWorld()

            # nothing found in the given file
            else:
                raise ConfigurationError("No world configuration found in file")

        # open file error
        except IOError:
            raise ConfigurationError("Cannot open given file")

        # extract position (x, y) from line error
        except ConfigurationError as confError:
            raise confError



    def __initializeWorld(self):
        for key in self.configDict.keys():
            print key, self.configDict[key]
            if self.configDict[key] is None or self.configDict[key] == []:
                raise ConfigurationError("%s configuration is missing" % key)

        # use a two-dimension array to store the state of world
        self.column = self.configDict["mapSize"][0]
        self.row = self.configDict["mapSize"][1]
        self.world = [[''] * self.row for i in range(self.column)]

        try:
            # place all elements into the "world" array
            for key in self.configDict.keys():
                if key == "agent" or key == "wumpus":
                    firstLetter = key[0].upper()
                    self.placeSymbol(self.configDict[key], firstLetter)

                elif key == "goal":
                    firstTwoLetters = key[:2].upper()
                    self.placeSymbol(self.configDict[key], firstTwoLetters)

                elif key == "breeze" or key == "gold" or key == "pit" or key == "stench":
                    for elementPosition in self.configDict[key]:
                        self.placeSymbol(elementPosition, key[0].upper())

                elif key == "mapSize":
                    pass
                else:
                    raise ConfigurationError("Unexpected key found in configDict")
            self.initialized = True

        except ConfigurationError as confError:
            raise confError


    def placeSymbol(self, position, symbol):
        posX = position[0]
        posY = position[1]
        if (symbol == "G" and self.world[posX-1][posY-1].find("W") != -1) \
                or (symbol == "W" and self.world[posX-1][posY-1].replace("GO", "@").find("G") != -1):
            raise ConfigurationError("Cannot place a gold with wumpus together!")
        else:
            self.world[posX-1][posY-1] = self.world[posX-1][posY-1] + "/" + symbol


    @staticmethod
    def extractPosition(confStr, confSymbol):
        line = confStr.strip().replace(confSymbol,"")
        x, y = None, None
        if line.find(",") != -1:
            x, y = [int(i) for i in line.split(",")]
        else:
            if len(line) == 2:
                x = int(line[0])
                y = int(line[1])
        if (x is not None) and (y is not None):
            return x, y
        else:
            raise ConfigurationError("Cannot extract %s configuration from line %s" % (confSymbol, confStr))


# Exception class created to support WumpusWorld initialization checking
class ConfigurationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


