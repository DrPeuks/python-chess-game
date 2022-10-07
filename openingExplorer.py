import chess
import json
import random
import subprocess




levelRatings = {
    1: "1600",
    2: "1600,1800",
    3: "1800,2000",
    4: "1800,2000,2200",
    5: "1800,2000,2200",
    6: "2000,2200,2500",
    7: "2200,2500",
    8: "2500"
}


level_winRateDeviation = {
    1: .20,
    2: .25,
    3: .32,
    4: .40,
    5: .45,
    6: .50,
    7: .50,
    8: .55
}


def get_opening_move(engineLevel, fen, turn):


     # Model
    "https://explorer.lichess.ovh/lichess?variant=standard&speeds=blitz,rapid,classical&ratings=2200,2500&fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201"


    defaultFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    text = "https://explorer.lichess.ovh/lichess?variant=standard&speeds=rapid,classical&ratings="+levelRatings[engineLevel]+"&fen="

    _fen = fen.split()
    finalFen = ""


    compText = "https://explorer.lichess.ovh/lichess?variant=standard&speeds=rapid,classical&ratings="+levelRatings[engineLevel]+"&fen="
    finalCompFen = ""
    for el in defaultFen.split():
        finalCompFen += el + "%20"
    for l in range(3):
        finalCompFen = finalCompFen.rstrip(finalCompFen[-1])
    compText += finalCompFen




    for el in _fen:
        finalFen += el + "%20"

    for l in range(3):
        finalFen = finalFen.rstrip(finalFen[-1])

    text += finalFen
    data = subprocess.check_output(['curl', text])

    data = json.loads(data)


    compData = subprocess.check_output(['curl', compText])
    compData = json.loads(compData)




    # get an appropriate opening move according to the number of games won with each move
    # if more than 50% of the games have been then return the move
    # else choose another random move until end condition has been reached

    if turn == True:
        turn = 'white'
    else:
        turn = 'black'

    totalStartGames = 0
    for op in compData['moves']:
        totalStartGames += (op['white'] + op['black'] + op['draws'])


    openings = []
    for op in data['moves']:
        total = op['white'] + op['black'] + op['draws']
        #print(f"{totalStartGames}  {total}  makes  {total / totalStartGames}")
        rate = op[turn] / total

        if rate >= level_winRateDeviation[engineLevel]:
            if total / totalStartGames >= .0005:
                openings.append(op['uci'])
        else:
            pass

    if len(openings) == 0:
        return (False, '')

    return (True, random.choice(openings))





#openings = get_opening_move(8, 'r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1', 0)




