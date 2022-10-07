import random


finalStr = ""
movesList = []
moveLog = "d2d4 d7d5 c2c4"


def getOpening(mvLog, file):

    with open(file) as _file:

        goodOpenings = []

        for line in _file:
            finalOpening = ''
            _opening = line.split()
            _opening.pop(0)
            for move in _opening:
                finalOpening += move + ' '
            if finalOpening.startswith(mvLog):
                goodOpenings.append(finalOpening)

        index = random.randint(0, len(goodOpenings)-1)

        return goodOpenings[index]


print(getOpening(moveLog, 'opening-books/bookfish_opening_seqs_12.txt'))
