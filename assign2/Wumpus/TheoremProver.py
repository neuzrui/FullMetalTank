import shlex

__author__ = 'Rui Zhang'

from string import Template
import subprocess

class TheoremProver(object):

    p9_input_template_path = "./p9_input_template.txt"

    def __init__(self, row, col, path = "./prover9"):
        self.row = row
        self.col = col
        self.binaryPath = path
        self.nearbyFacts = self.generateNearbyFacts()
        self.knowledge = ""
        self.theorem = ""
        self.tempInput = self.getTempInput()

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

    def getTempInput(self):
        templateFile = file(self.p9_input_template_path)
        templateStr = templateFile.read()
        templateFile.close()
        return Template(templateStr)


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

    def checkTheorem(self, knowledge, theorem):
        self.knowledge = knowledge
        self.theorem = theorem
        if self.generateP9Input():
            # try:
            #     outputStr = subprocess.check_output([self.binaryPath, "-f", "./p9_input.txt"])
            #     if outputStr.find("THEOREM PROVED") != -1:
            #         return True
            #     else:
            #         return False
            # except subprocess.CalledProcessError:
            #     return False
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
    # knowledge = "-Stench(1,1).\n-Breeze(1,1).\n-Stench(2,1).\nBreeze(2,1).\nStench(1,2).\n-Breeze(1,2).\n"
    # theorem = "-Wumpus(1,2)."
    knowledge = "-Breeze(1,1).\n-Stench(1,1)."
    theorem = "-Pit(1,2)."
    if tp.checkTheorem(knowledge, theorem):
        print "proved"











