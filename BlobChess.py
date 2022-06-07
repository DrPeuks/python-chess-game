import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # hide pygame welcome message because its annoying :D

import chess
import chess.engine
import platform
import pygame
from random import randint
import stockfish
import subprocess
import sys
from tkinter import *
from tkinter import messagebox


































class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.whiteToMove = True
        self.moveLog = []





    """
    This takes a move as a parameter and executes it [this will not work for castling, pawn promotion and en-passant
    """
    def makeMove(self, move):

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update the king location if it is moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)


    """
    Undo the last move made
    """
    def undoMove(self):
        if len(self.moveLog) != 0: # make sure that there is a move to undo lol
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endCol) == 2:
                self.enPassantPossible = ()







class Move:


    ranksToRow = {"1": 7, "2": 6, "3": 5, "4": 4,
                  "5": 3, "6": 2, "7": 1, "8": 0}
    rowToranks = {v: k for k, v in ranksToRow.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                  "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]



        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol



    """
    Overridding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False



    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowToranks[r]


































pygame.font.init()


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
MOVELOG_WIDTH = 600
PLAYERSPOLICE = pygame.font.SysFont("Consolas", 20)
POLICE = pygame.font.SysFont("Consolas", 32)
gameOver = False
winList = []
winner = ""
lc0_path = ""
path_to_fairyStockfish = ""
path_to_maia = ""

stockfishLevel = 0
playersNamesTexts = []

pawnPromotionList = []

completeMoveLog = ""
displayMoveLog = False



files = ["a", "b", "c", "d", "e", "f", "g", "h"]
rows  = ["8", "7", "6", "5", "4", "3", "2", "1"]
rows_int = [8, 7, 6, 5, 4, 3, 2, 1]
fileToX = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
rowToY =  {"8": 0, "7": 1, "6": 2, "5": 3, "4": 4, "3": 5, "2": 6, "1": 7}




'''
Stockfish settings
'''


stockfish_levels = [  # each list corresponding to the level contains skill level (1~20), depth and time for each move in milliseconds
  # [skillLevel, depth, time(ms), elo rating]
    [3, 1, 50, 500],
    [6, 2, 100, 800],
    [9, 3, 150, 1100],
    [11, 4, 200, 1400],
    [14, 6, 250, 1700],
    [17, 8, 300, 1900],
    [20, 10, 350, 2100],
    [20, 12, 400, 2250],
    [20, 20, 700]
]

if platform.system() == "win32":
    path_to_fairyStockfish = "fairy-stockfish/fairy-stockfish-largeboard_win64.exe"
    lc0_path = "lc0-windows/lc0.exe"
    path_to_maia = "lc0/windows/"
elif platform.system() == "Linux":
    path_to_fairyStockfish = "fairy-stockfish/fairy-stockfish-linux-x86_64"
    lc0_path = "lc0-linux/build/release/lc0"
    path_to_maia = "lc0-linux/build/release/"


whitePlayerImage = pygame.transform.scale(pygame.image.load("images/whitePlayer.png"), (20, 20))


boardImage = pygame.transform.scale(pygame.image.load("images/wood4.jpg"), (WIDTH, WIDTH))


def random_move(board):
    if board.legal_moves.count() > 0:
        validMoves = []
        for move in board.legal_moves:
            validMoves.append(move)

        return validMoves
    else:
        return "0"


def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))



def lc0_command(process, command):

    process.stdin.write(f"{command}\n")



def lc0_gestBestMove(path_to_lc0, _mvList, wtm, eloList):

    bestMove = ""

    mvList = ""
    for m in _mvList:
        mvList += m+" "


    if wtm:
        p = subprocess.Popen([path_to_lc0, f"--weights={path_to_maia}/maia-{eloList[0]}.pb.gz"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, text=True)
    else:
        p = subprocess.Popen([path_to_lc0, f"--weights={path_to_maia}/maia-{eloList[1]}.pb.gz"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, text=True)

    lc0_command(p, "position startpos moves {}".format(mvList))
    lc0_command(p, "go nodes 1")


    for line in iter(p.stdout.readline, ''):
   
    
        line = line.strip()

        if line.startswith("bestmove"):

            bestMove = line.split()[1].strip()
            break

    
    lc0_command(p, "quit")

    # Make sure process p is terminated, if not lets try to close it again
    try:
        p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()


    return bestMove
    



def main():




    # This is the window that pops up when the game starts and that lets the user configure the game
    # Instead of a non-friendly command-line interface for noobs :D

    popupWindow = Tk()
    popupWindow.title("Blob Chess! Game setup")


    maia_lvllist = ['1100', '1500', '1900']


    whitePlayer_intvar = IntVar()
    whitePlayer_choiceFrame = LabelFrame(popupWindow, text='Who plays as White?')
    whitePlayer_choiceFrame.grid(row=1, column=0, padx=40, pady=20)
    whitePlayer_lvlIntVar = IntVar()
    whitePlayer_nameTextVar = StringVar()
    whitePlayer_maiaELO = IntVar()


    Radiobutton(whitePlayer_choiceFrame, text='User (you)', variable=whitePlayer_intvar, value=0).grid(row=0, column=0)
    Radiobutton(whitePlayer_choiceFrame, text='Fairy Stocfish', variable=whitePlayer_intvar, value=1).grid(row=1, column=0)
    Radiobutton(whitePlayer_choiceFrame, text='Random Move', variable=whitePlayer_intvar, value=2).grid(row=2, column=0)
    Radiobutton(whitePlayer_choiceFrame, text="Maia", variable=whitePlayer_intvar, value=3).grid(row=3, column=0)
    Label(whitePlayer_choiceFrame, fg="red", text="Select level :").grid(row=1, column=1)
    Scale(whitePlayer_choiceFrame, from_=1, to=8, variable=whitePlayer_lvlIntVar, orient=HORIZONTAL).grid(row=1, column=2)
    Label(whitePlayer_choiceFrame, fg="red", text="What's your name? ").grid(row=0, column=1)
    Entry(whitePlayer_choiceFrame, textvariable=whitePlayer_nameTextVar).grid(row=0, column=2)
    Label(whitePlayer_choiceFrame, fg="red", text="Select ELO ").grid(row=3, column=1)
    Radiobutton(whitePlayer_choiceFrame, text="1100", variable=whitePlayer_maiaELO, value=0).grid(row=3, column=2)
    Radiobutton(whitePlayer_choiceFrame, text="1500", variable=whitePlayer_maiaELO, value=1).grid(row=3, column=3)
    Radiobutton(whitePlayer_choiceFrame, text="1900", variable=whitePlayer_maiaELO, value=2).grid(row=3, column=4)



    blackPlayer_intvar = IntVar()
    blackPlayer_choiceFrame = LabelFrame(popupWindow, text='Who plays as black?')
    blackPlayer_choiceFrame.grid(row=1, column=1, padx=40, pady=20)
    blackPlayer_lvlIntVar = IntVar()
    blackPlayer_nameTextVar = StringVar()
    blackPlayer_maiaELO = IntVar()

    Radiobutton(blackPlayer_choiceFrame, text='User (you)', variable=blackPlayer_intvar, value=0).grid(row=0, column=0)
    Radiobutton(blackPlayer_choiceFrame, text='Fairy Stocfish', variable=blackPlayer_intvar, value=1).grid(row=1, column=0)
    Radiobutton(blackPlayer_choiceFrame, text='Random Move', variable=blackPlayer_intvar, value=2).grid(row=2, column=0)
    Radiobutton(blackPlayer_choiceFrame, text="Maia", variable=blackPlayer_intvar, value=3).grid(row=3, column=0)
    Label(blackPlayer_choiceFrame, fg="red", text="Select level :").grid(row=1, column=1)
    Scale(blackPlayer_choiceFrame, from_=1, to=8, variable=blackPlayer_lvlIntVar, orient=HORIZONTAL).grid(row=1, column=2)
    Label(blackPlayer_choiceFrame, fg="red", text="What's your name? ").grid(row=0, column=1)
    Entry(blackPlayer_choiceFrame, textvariable=blackPlayer_nameTextVar).grid(row=0, column=2)
    Label(blackPlayer_choiceFrame, fg="red", text="Select ELO ").grid(row=3, column=1)
    Radiobutton(blackPlayer_choiceFrame, text="1100", variable=blackPlayer_maiaELO, value=0).grid(row=3, column=2)
    Radiobutton(blackPlayer_choiceFrame, text="1500", variable=blackPlayer_maiaELO, value=1).grid(row=3, column=3)
    Radiobutton(blackPlayer_choiceFrame, text="1900", variable=blackPlayer_maiaELO, value=2).grid(row=3, column=4)


    goButton = Button(popupWindow, text="go", command=popupWindow.destroy).grid(row=3, column=0)


    useNNUE_eval = IntVar(value=1)
    useNNUE_eval_checkbutton = Checkbutton(popupWindow, text="Use NNUE evaluation, displayed at the top right corner of the window \n(this will slow down the application a bit)", onvalue=1, offvalue=0, variable=useNNUE_eval).grid(row=2, column=0)

    popupWindow.mainloop()

    lc0_moveList = []


    whitePlayerChoice_ = whitePlayer_intvar.get()
    blackPlayerChoice_ = blackPlayer_intvar.get()




    _blackPlayer = ""
    _whitePlayer = ""

    maia_whiteElo = ""
    maia_blackElo = ""

    # Configure the players

    if whitePlayerChoice_ == 0:
        whitePlayerName = str(whitePlayer_nameTextVar.get())
        whitePlayer = "User"
        _whitePlayer = whitePlayerName
    elif whitePlayerChoice_ == 1:
        whitePlayer = "Stockfish"
        whiteEngine = chess.engine.SimpleEngine.popen_uci(path_to_fairyStockfish)
    elif whitePlayerChoice_ == 2:
        whitePlayer= "Random Move AI"
        _whitePlayer = "Random Move"
    elif whitePlayerChoice_ == 3:
        whitePlayer = "Maia Chess"
        maia_whiteElo = maia_lvllist[whitePlayer_maiaELO.get()]
        _whitePlayer = f"Maia {maia_whiteElo}"

    if blackPlayerChoice_ == 0:
        blackPlayerName = str(blackPlayer_nameTextVar.get())
        blackPlayer = "User"
        _blackPlayer = blackPlayerName
    elif blackPlayerChoice_ == 1:
        blackPlayer = "Stockfish"
        blackEngine = chess.engine.SimpleEngine.popen_uci(path_to_fairyStockfish)
    elif blackPlayerChoice_ == 2:
        blackPlayer= "Random Move AI"
        _blackPlayer = "Random Move"
    elif blackPlayerChoice_ == 3:
        blackPlayer = "Maia Chess"
        maia_blackElo = maia_lvllist[blackPlayer_maiaELO.get()]
        _blackPlayer = f"Maia {maia_blackElo}"
    else:
        blackPlayer = "Stockfish"


    whiteEngine_depth = 0
    whiteEngine_time  = 0
    blackEngine_depth = 0
    blackEngine_time  = 0

    

    _useNNUE = useNNUE_eval.get()
    enable_NNUE = False

    if _useNNUE == 1:
        enable_NNUE = True
        if platform.system() == "win32":
            analysisEngine = stockfish.Stockfish("stockfish/stockfish_14.1.exe")
        elif platform.system() == "Linux":
            analysisEngine = stockfish.Stockfish("stockfish/stockfish-linux-x86_64")
    else:
        enable_NNUE = False
    



    # Configure the Fairy Stockfish levels if needed

    enginePlaying = (whitePlayer == "Stockfish") or (blackPlayer == "Stockfish")

    if whitePlayer == "Stockfish":
        whiteStockfishLevel = whitePlayer_lvlIntVar.get()
        _l = whiteStockfishLevel - 1
        whiteEngine.configure(
            {
                "Skill Level": stockfish_levels[_l][0],
                "UCI_LimitStrength": True,
                "UCI_Elo": stockfish_levels[_l][3],
                "Use NNUE": False
            }
        )
        whiteEngine_depth = stockfish_levels[_l][1]

    if blackPlayer == "Stockfish":
        blackStockfishLevel = blackPlayer_lvlIntVar.get()
        _l = blackStockfishLevel - 1
        blackEngine.configure(
            {
                "Skill Level": stockfish_levels[_l][0],
                "UCI_LimitStrength": True,
                "UCI_Elo": stockfish_levels[_l][3],
                "Use NNUE": False
            }
        )
        blackEngine_depth = stockfish_levels[_l][1]


    
    coreBoard = chess.Board()
    

    squaresToHighlight = []
    destinationSquaresToHighlight = []


    if enable_NNUE:
        analysisEngine.set_fen_position(coreBoard.fen())
    b = chess.Board()

    font = pygame.font.SysFont("Helvetica", 17)
    moveText = ""
    moveLogSurfaces = []
    moveLog = []


    if whitePlayer == "Stockfish":
        stockfishPlayer = "Stockfish level {}".format(whiteStockfishLevel)
        _whitePlayer = stockfishPlayer
    if blackPlayer == "Stockfish":
        stockfishPlayer = "Stockfish level {}".format(blackStockfishLevel)
        _blackPlayer = stockfishPlayer



    playersNamesTexts.append(PLAYERSPOLICE.render(_whitePlayer, 1, (255, 255, 255)))
    playersNamesTexts.append(PLAYERSPOLICE.render(_blackPlayer, 1, (255, 255, 255)))

    pgnBeginning = f"[White \"{_whitePlayer}\"]\n[Black \"{_blackPlayer}\"]\n\n"


    pygame.init()
    screen = pygame.display.set_mode((WIDTH+MOVELOG_WIDTH, HEIGHT+50))
    pygame.display.set_caption("Blob Chess!")
    display_icon = pygame.image.load("images/horsey.jpeg")
    pygame.display.set_icon(display_icon)
    gs = GameState()
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))

    hasToGen_pml = True # check if we have to generate the pawm promotion list after a player moves
                        # so that we don't generate it each iteration, which would slow down the game

    moveMade = False
    whiteToMove = True
    if whiteToMove:
        turn = "w"
    else:
        turn = "b"

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    turnPlayed = False

    if enable_NNUE:
        engineEval = analysisEngine.get_evaluation()
        if engineEval['type'] == "cp":
            if engineEval['value'] > 0:
                _text = "+"
            elif engineEval['value'] < 0:
                _text = ""
            value = engineEval['value'] / 100
        elif engineEval['type'] == "mate":
            if engineEval['value'] != 0:
                _text = "#"
                value = engineEval['value']
            elif engineEval['value'] == 0:
                _text = "-"
                value = None
        if value != None:
            evalText = POLICE.render(str(_text + str(value)), 1, (255, 255, 255))
        else:
            evalText = POLICE.render(str(_text), 1, (255, 255, 255))

    while running == True:


        if hasToGen_pml == True:
       	    pawnPromotionList = []
            for move in coreBoard.legal_moves:
                if len(str(move)) == 5:
                    m = move.__str__()
                    pawnPromotionList.append(m[0] + m[1] + m[2] + m[3])
            hasToGen_pml = False



        for e in pygame.event.get():
            
            if e.type == pygame.QUIT:

                running = False

            # mouse handling
            elif e.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE

                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)

                if len(playerClicks) == 1 and ((whitePlayer == "User" and turn == "w") or (blackPlayer == "User" and turn == "b")) and (not turnPlayed):
                    
                    squareClicked = files[playerClicks[0][1]] + rows[playerClicks[0][0]]

                    for m in coreBoard.legal_moves:

                        m = str(m)
                        if (m[0]+m[1]) == squareClicked:

                            squaresToHighlight = [[playerClicks[0][1], playerClicks[0][0]]]
                            
                            destinationSquaresToHighlight.append([fileToX[m[2]], rowToY[m[3]]])

                            


                if len(playerClicks) == 3:

                    playerClicks = []    
                

                if len(playerClicks) == 2 and ((whitePlayer == "User" and turn == "w") or (blackPlayer == "User" and turn == "b")) and (not turnPlayed):
                    squaresToHighlight = []
                    destinationSquaresToHighlight = []
                    if (playerClicks[1][0] <= 7) and (playerClicks[1][1] <= 7) and (playerClicks[0][0] <= 7) and (playerClicks[0][1] <= 7):
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        if chess.Move.from_uci(move.getChessNotation()) in coreBoard.legal_moves:
                            gs.makeMove(move)
                            moveLog.append(move.getChessNotation())
                            lc0_moveList.append(move.getChessNotation())
                            coreBoard.push_uci(move.getChessNotation())
                            drawGameState(screen, gs.board, coreBoard, squaresToHighlight, destinationSquaresToHighlight)

                            if enable_NNUE:
                                analysisEngine.set_fen_position(coreBoard.fen())
                            moveMade = True
                            sqSelected = () # reset user clicks
                            playerClicks = []

                            turnPlayed = True
                            whiteToMove = not whiteToMove
                            if whiteToMove:
                                turn = "w"
                            else:
                                turn = "b"


                            hasToGen_pml = True



                        if str(chess.Move.from_uci(move.getChessNotation())) in pawnPromotionList:
                            ws = Tk()
                            ws.title('Duh! A pawn promotion!')
                            ws.geometry('200x140')
                            ws.configure(bg='#dddddd')
                            var = IntVar()
                            frame = LabelFrame(ws, text='Select piece', padx=50, bg='#dddddd')
                            frame.pack()
                            Radiobutton(frame, text="Queen", variable=var, value=1).pack(anchor=W)
                            Radiobutton(frame, text="Rook", variable=var, value=2).pack(anchor=W)
                            Radiobutton(frame, text="Knight", variable=var, value=3).pack(anchor=W)
                            Radiobutton(frame, text="Bishop", variable=var, value=4).pack(anchor=W)
                            Button(ws, text="Promote!", command=ws.destroy).pack()

                            ws.mainloop()

                            choice = var.get()
                            _move = ""
                            if choice == 1:
                                _move = str(chess.Move.from_uci(move.getChessNotation())) + "q"
                            elif choice == 2:
                                _move = str(chess.Move.from_uci(move.getChessNotation())) + "r"
                            elif choice == 3:
                                _move = str(chess.Move.from_uci(move.getChessNotation())) + "n"
                            if choice == 4:
                                _move = str(chess.Move.from_uci(move.getChessNotation())) + "b"
                            else:
                                _move = str(chess.Move.from_uci(move.getChessNotation())) + "q"

                            moveLog.append(_move)

                            coreBoard.push_uci(_move)
                            drawGameState(screen, gs.board, coreBoard, squaresToHighlight, destinationSquaresToHighlight)
                            lc0_moveList.append(_move)
                            if enable_NNUE:
                                analysisEngine.set_fen_position(coreBoard.fen())
                            moveMade = True
                            sqSelected = () # reset user clicks
                            playerClicks = []

                            turnPlayed = True
                            whiteToMove = not whiteToMove
                            if whiteToMove:
                                turn = "w"
                            else:
                                turn = "b"


                            hasToGen_pml = True






                    if not moveMade:
                        playerClicks = [sqSelected]

            # keyboard handling
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    
                    moveLog.pop(len(moveLog)-1)
                    coreBoard.pop()
                    moveMade = True
                    if enable_NNUE:
                        analysisEngine.set_fen_position(coreBoard.fen())

            




        if (whitePlayer == "Stockfish" and turn == "w") and (not turnPlayed):

            result = str(whiteEngine.play(coreBoard, limit=chess.engine.Limit(depth=whiteEngine_depth, time=whiteEngine_time)).move)

            lc0_moveList.append(result)

            coreBoard.push(chess.Move.from_uci(result))
            moveLog.append(str(result))

            if enable_NNUE:
                analysisEngine.set_fen_position(coreBoard.fen())
            turnPlayed = True
            whiteToMove = not whiteToMove
            if whiteToMove:
                turn = "w"
            else:
                turn = "b"

            hasToGen_pml = True

        elif (blackPlayer == "Stockfish" and turn == "b") and (not turnPlayed):

            result = str(blackEngine.play(coreBoard, limit=chess.engine.Limit(depth=blackEngine_depth, time=blackEngine_time)).move)

            lc0_moveList.append(result)

            coreBoard.push(chess.Move.from_uci(result))
            moveLog.append(str(result))

            if enable_NNUE:
                analysisEngine.set_fen_position(coreBoard.fen())
            turnPlayed = True
            whiteToMove = not whiteToMove
            if whiteToMove:
                turn = "w"
            else:
                turn = "b"

            hasToGen_pml = True


        if (whitePlayer == "Random Move AI" and whiteToMove) or (blackPlayer == "Random Move AI" and not whiteToMove) and (not turnPlayed):
            validMoves = random_move(coreBoard)
            result = validMoves[randint(0, len(validMoves))-1]

            lc0_moveList.append(result)

            if result != "0":
                coreBoard.push(chess.Move.from_uci(str(result)))
                moveLog.append(str(result))
            else:
                pass
            turnPlayed = True
            whiteToMove = not whiteToMove

            if enable_NNUE:
                analysisEngine.set_fen_position(coreBoard.fen())


            hasToGen_pml = True



        if (whitePlayer == "Maia Chess" and whiteToMove) or (blackPlayer == "Maia Chess" and not whiteToMove) and not turnPlayed:


            result = lc0_gestBestMove(lc0_path, lc0_moveList, whiteToMove, [maia_whiteElo, maia_blackElo]).__str__()

            lc0_moveList.append(result)

            coreBoard.push(chess.Move.from_uci(result))
            moveLog.append(result)

            turnPlayed = True
            whiteToMove = not whiteToMove

            if enable_NNUE:
                analysisEngine.set_fen_position(coreBoard.fen())

            hasToGen_pml = True



        if moveMade:
            moveMade = False

        if whiteToMove:
            turn = "w"
        else:
            turn = "b"

        if enable_NNUE:
            analysisEngine.set_fen_position(coreBoard.fen())





        gameOver = False
        endText_render               = False
        drawText_render_stalemate    = False
        drawText_render_insufficient = False
        drawText_render_repetition   = False
        if coreBoard.is_checkmate():
            winner = ""
            if coreBoard.outcome().winner:
                winner = "White"
                winList = [1, 0]
            else:
                winner = "Black"
                winList = [0, 1]
            
            endText_render = True

            running = False
            gameOver = True
            
        elif coreBoard.is_stalemate():
            running = False
            gameOver = True
            drawText_render_stalemate = True
        elif coreBoard.is_fivefold_repetition():
            running = False
            gameOver = True
            drawText_render_repetition = True
        elif coreBoard.is_insufficient_material():
            gameOver = True
            running = False
            drawText_render_insufficient = True




        
        b.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        completeMoveLog = b.variation_san([chess.Move.from_uci(m) for m in moveLog])

        if gameOver:
            displayMoveLog = True

        # print the move log with lines
        index = 0
        tempLine = ""
        for l in completeMoveLog:
            moveLogSurfaces.append("")
            if font.size(tempLine+l)[0] <= MOVELOG_WIDTH:
                tempLine += l
                moveLogSurfaces[index] = tempLine
            if font.size(tempLine+l)[0] > MOVELOG_WIDTH:
                moveLogSurfaces[index] = tempLine
                tempLine = ""
                index += 1








        screen.fill((0, 0, 0))

        if enable_NNUE:
            screen.blit(evalText, (WIDTH + 40, 0))



        lineNB = 1
        for line in moveLogSurfaces:
            _line = font.render(line, 1, (255, 255, 255))
            if lineNB == 1:
                screen.blit(_line, (WIDTH, 50))
            else:
                screen.blit(_line, (WIDTH, 17*lineNB+(17*2+5)))
            lineNB += 1
        drawGameState(screen, gs.board, coreBoard, squaresToHighlight, destinationSquaresToHighlight)


        if endText_render:
            
            endText = POLICE.render("Checkmate!", 1, (0, 255, 0))
            screen.blit(endText, (SQ_SIZE*8+80, 0))
            if coreBoard.outcome().winner:
                result = ["1", "0"]
            else:
                result = ["0", "1"]
            whiteResultText = PLAYERSPOLICE.render(result[0], 1, (255, 255, 255))
            screen.blit(whiteResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[0])[0], SQ_SIZE*8))
            blackResultText = PLAYERSPOLICE.render(result[1], 1, (255, 255, 255))
            screen.blit(blackResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[1])[0], (SQ_SIZE*8)+(PLAYERSPOLICE.size(result[1])[1])))
            if displayMoveLog:
                root = Tk()
                root.title("Game PGN")
                ent = Text(root, height=20, borderwidth=0)
                ent.insert(1.0, pgnBeginning+completeMoveLog)
                ent.pack()
                ent.configure(state="disabled")
                ent.configure(inactiveselectbackground=ent.cget("selectbackground"))
                root.mainloop()
        elif drawText_render_stalemate:
            endText = POLICE.render("STALEMATE HAHAHA", 1, (0, 255, 0))
            screen.blit(endText, (SQ_SIZE*8+80, 0))
            result = ["1/2", "1/2"]
            whiteResultText = PLAYERSPOLICE.render(result[0], 1, (255, 255, 255))
            screen.blit(whiteResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[0])[0], SQ_SIZE*8))
            blackResultText = PLAYERSPOLICE.render(result[1], 1, (255, 255, 255))
            screen.blit(blackResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[1])[0], (SQ_SIZE*8)+(PLAYERSPOLICE.size(result[1])[1])))
            if displayMoveLog:
                root = Tk()
                root.title("Game PGN")
                ent = Text(root, height=20, borderwidth=0)
                ent.insert(1.0, pgnBeginning+completeMoveLog)
                ent.pack()
                ent.configure(state="disabled")
                ent.configure(inactiveselectbackground=ent.cget("selectbackground"))
                root.mainloop()
        elif drawText_render_repetition:
            endText = POLICE.render("Fivefold repetition. Draw.", 1, (0, 255, 0))
            screen.blit(endText, (SQ_SIZE*8+80, 0))
            result = ["1/2", "1/2"]
            whiteResultText = PLAYERSPOLICE.render(result[0], 1, (255, 255, 255))
            screen.blit(whiteResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[0])[0], SQ_SIZE*8))
            blackResultText = PLAYERSPOLICE.render(result[1], 1, (255, 255, 255))
            screen.blit(blackResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[1])[0], (SQ_SIZE*8)+(PLAYERSPOLICE.size(result[1])[1])))
            if displayMoveLog:
                root = Tk()
                root.title("Game PGN")
                ent = Text(root, height=20, borderwidth=0)
                ent.insert(1.0, pgnBeginning+completeMoveLog)
                ent.pack()
                ent.configure(state="disabled")
                ent.configure(inactiveselectbackground=ent.cget("selectbackground"))
                root.mainloop()
        elif drawText_render_insufficient:
            endText = POLICE.render("Insufficient material. Draw", 1, (0, 255, 0))
            screen.blit(endText, (SQ_SIZE*8+80, 0))
            result = ["1/2", "1/2"]
            whiteResultText = PLAYERSPOLICE.render(result[0], 1, (255, 255, 255))
            screen.blit(whiteResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[0])[0], SQ_SIZE*8))
            blackResultText = PLAYERSPOLICE.render(result[1], 1, (255, 255, 255))
            screen.blit(blackResultText, ((SQ_SIZE*8)-PLAYERSPOLICE.size(result[1])[0], (SQ_SIZE*8)+(PLAYERSPOLICE.size(result[1])[1])))
            if displayMoveLog:
                root = Tk()
                root.title("Game PGN")
                ent = Text(root, height=20, borderwidth=0)
                ent.insert(1.0, pgnBeginning+completeMoveLog)
                ent.pack()
                ent.configure(state="disabled")
                ent.configure(inactiveselectbackground=ent.cget("selectbackground"))
                root.mainloop()
        
        
        
        


        pygame.display.update()

        



        # format the evaluation text

        if enable_NNUE:
            if turnPlayed:
                engineEval = analysisEngine.get_evaluation()
                if engineEval['type'] == "cp":
                    if engineEval['value'] > 0:
                        _text = "+"
                    elif engineEval['value'] < 0:
                        _text = ""
                    value = engineEval['value']/100
                elif engineEval['type'] == "mate":
                    if engineEval['value'] != 0:
                        _text = "#"
                        value = engineEval['value']
                    elif engineEval['value'] == 0:
                        _text = "-"
                        value = None
                if value != None:
                    evalText = POLICE.render(str(_text+str(value)), 1, (255, 255, 255))
                else:
                    evalText = POLICE.render(str(_text), 1, (255, 255, 255))


        turnPlayed = False

        if enable_NNUE:
            screen.blit(evalText, (WIDTH + 40, 0))




def drawGameState(screen, b, _b, squares, destSquares):
    drawBoard(screen)
    if len(squares) > 0:
        pygame.draw.rect(screen, (255, 0, 0), (squares[0][0]*SQ_SIZE+1, squares[0][1]*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    if len(destSquares) > 0:
        for r in destSquares:
            pygame.draw.rect(screen, (205, 127, 50), (r[0]*SQ_SIZE, r[1]*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    drawPieces(screen, b, _b)
    screen.blit(whitePlayerImage, pygame.Rect(0, HEIGHT+2.5, 20, 20))




def drawBoard(screen):

    # here draw the players' names on the bottom left of the window
    screen.blit(boardImage, pygame.Rect(0, 0, WIDTH, WIDTH))
    pygame.draw.circle(screen, (255, 255, 255), (10, HEIGHT+35), 10, 1)
    screen.blit(playersNamesTexts[0], (25, HEIGHT+3))
    screen.blit(playersNamesTexts[1], (25, HEIGHT+26))






def drawPieces(screen, board, _board):
    index = 0
    for r in range(8):
        for c in range(8):
            while True:
                _p = str(_board)[index]
                if _p == "\n" or _p == " ":
                    index += 1
                else:
                    break
            if _p == ".":
                _p = "--"
            if _p.islower():
                _p = "b" + str.upper(_p)
            elif _p.isupper():
                _p = "w" + str.upper(_p)
            board[r][c] = _p
            index += 1

    for r in range(DIMENSION):
        for c in range(DIMENSION):
                piece = board[r][c]
                if piece != "--":
                    screen.blit(IMAGES[piece], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))





if __name__ == "__main__":
    main()
    pygame.init()
    _quit=False
        

    while True:
        pygame.display.update() 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                _quit=True
        if _quit:
            break
        
os._exit(0)
