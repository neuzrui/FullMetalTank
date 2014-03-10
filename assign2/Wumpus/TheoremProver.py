__author__ = 'Rui Zhang'

import shlex
from string import Template
import subprocess

class TheoremProver(object):

    p9_input_template_path = "./p9_input_template.txt"

    # init the prover
    def __init__(self, row, col, path = "./prover9"):
        self.row = row
        self.col = col
        self.binaryPath = path
        self.nearbyFacts = self.generateNearbyFacts()
        self.knowledge = ""
        self.theorem = ""
        self.tempInput = self.getTempInput()

    # generate NearbyX and NearbyY logic
    def generateNearbyFacts(self):
        facts = ""
        facts += "all X (NearbyX(1,X) <-> X=2).\n"
        for i in range(2, self.col):
            facts += "all X (NearbyX(%d,X) <-> X=%d | X=%d).\n" % (i, i-1, i+1)
        facts += "all X (NearbyX(%d,X) <-> X=%d).\n" % (self.col, self.col - 1)

        facts += "all Y (NearbyY(1,Y) <-> Y=2).\n"
        for i in range(2,self.row):
            facts += "all Y (NearbyY(%d,Y) <-> Y=%d | Y=%d).\n" % (i, i-1, i+1)
        facts += "all Y (NearbyY(%d,Y) <-> Y=%d).\n" % (self.row, self.row - 1)
        return facts

    # get p9 input file template
    def getTempInput(self):
        templateFile = file(self.p9_input_template_path)
        templateStr = templateFile.read()
        templateFile.close()
        return Template(templateStr)

    # substitute the variables in the template
    def generateP9Input(self):
        try:
            inputStr = self.tempInput.substitute(
                knowledge=self.knowledge,
                nearbyFacts=self.nearbyFacts,
                theorem=self.theorem)
            inputFile = file("./p9_input.txt", "w")
            inputFile.truncate()
            inputFile.write(inputStr)
            inputFile.close()
            return True
        except IOError:
            raise

    # check the theorem based on given knowledge
    def checkTheorem(self, knowledge, theorem):
        self.knowledge = knowledge
        self.theorem = theorem
        if self.generateP9Input():
            command = self.binaryPath + " -f ./p9_input.txt"
            args = shlex.split(command)
            prc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if prc.stdout.read().find('THEOREM PROVED') > 0:
                prc.kill()
                return True
            else:
                prc.kill()
                return False


if __name__ == "__main__":
    tp = TheoremProver(4,4)
    knowledge = "-Breeze(1,1).\n-Stench(1,1)."
    theorem = "-Pit(1,2)."
    if tp.checkTheorem(knowledge, theorem):
        print "proved"











