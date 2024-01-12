# %%
import chess
import chess.pgn
import matplotlib.pyplot as plt
from IPython.display import display
import matplotlib
from stockfish import Stockfish
matplotlib.rcParams.update(matplotlib.rcParamsDefault)

# %%

board=chess.Board()
board
    
# %%

class PSTAnalyzerPosition:
    def __init__(self):
        self.initStockfish()
        # store piece square tables in a dictionary
        # piece square tables are stored as a list of lists, for white
        # black piece square tables are the mirror image of the white tables
        # each list represents a rank
        # each element in the list represents a file
        # [0][0] is the a1 square, [0][1] is the b1 square, etc.
        # the element is a tuple of middle game and end game values
        # ranks A to D are explicitly defined
        # ranks E to H are defined by mirror flipping the rank
        # pawn tables are explicit for all ranks 2-7, empty for rank 1 and 8
        # get_pst(chess.PIECE_TYPE, chess.SQUARE) returns the tuple of values
        self.pst = {
            chess.KNIGHT:
            [[ (-175, -96), (-92,-65), (-74,-49), (-73,-21)],
            [ ( -77, -67), (-41,-54), (-27,-18), (-15,  8) ],
            [ ( -61, -40), (-17,-27), (  6, -8), ( 12, 29) ],
            [ ( -35, -35), (  8, -2), ( 40, 13), ( 49, 28) ],
            [ ( -34, -45), ( 13,-16), ( 44,  9), ( 51, 39) ],
            [ (  -9, -51), ( 22,-44), ( 58,-16), ( 53, 17) ],
            [ ( -67, -69), (-27,-50), (  4,-51), ( 37, 12) ],
            [ (-201,-100), (-83,-88), (-56,-56), (-26,-17) ]],
            chess.BISHOP:
            [[ (-37,-40), (-4 ,-21), ( -6,-26), (-16, -8) ],
            [ (-11,-26), (  6, -9), ( 13,-12), (  3,  1) ],
            [ (-5 ,-11), ( 15, -1), ( -4, -1), ( 12,  7) ],
            [ (-4 ,-14), (  8, -4), ( 18,  0), ( 27, 12) ],
            [ (-8 ,-12), ( 20, -1), ( 15,-10), ( 22, 11) ],
            [ (-11,-21), (  4,  4), (  1,  3), (  8,  4) ],
            [ (-12,-22), (-10,-14), (  4, -1), (  0,  1) ],
            [ (-34,-32), (  1,-29), (-10,-26), (-16,-17) ]],
            chess.ROOK:
            [[ (-31, -9), (-20,-13), (-14,-10), (-5, -9) ],
            [ (-21,-12), (-13, -9), ( -8, -1), ( 6, -2) ],
            [ (-25,  6), (-11, -8), ( -1, -2), ( 3, -6) ],
            [ (-13, -6), ( -5,  1), ( -4, -9), (-6,  7) ],
            [ (-27, -5), (-15,  8), ( -4,  7), ( 3, -6) ],
            [ (-22,  6), ( -2,  1), (  6, -7), (12, 10) ],
            [ ( -2,  4), ( 12,  5), ( 16, 20), (18, -5) ],
            [ (-17, 18), (-19,  0), ( -1, 19), ( 9, 13) ]],
            chess.QUEEN:
            [[ ( 3,-69), (-5,-57), (-5,-47), ( 4,-26) ],
            [ (-3,-54), ( 5,-31), ( 8,-22), (12, -4) ],
            [ (-3,-39), ( 6,-18), (13, -9), ( 7,  3) ],
            [ ( 4,-23), ( 5, -3), ( 9, 13), ( 8, 24) ],
            [ ( 0,-29), (14, -6), (12,  9), ( 5, 21) ],
            [ (-4,-38), (10,-18), ( 6,-11), ( 8,  1) ],
            [ (-5,-50), ( 6,-27), (10,-24), ( 8, -8) ],
            [ (-2,-74), (-2,-52), ( 1,-43), (-2,-34) ]],
            chess.KING:
            [[ (271,  1), (327, 45), (271, 85), (198, 76) ],
            [ (278, 53), (303,100), (234,133), (179,135) ],
            [ (195, 88), (258,130), (169,169), (120,175) ],
            [ (164,103), (190,156), (138,172), ( 98,172) ],
            [ (154, 96), (179,166), (105,199), ( 70,199) ],
            [ (123, 92), (145,172), ( 81,184), ( 31,191) ],
            [ ( 88, 47), (120,121), ( 65,116), ( 33,131) ],
            [ ( 59, 11), ( 89, 59), ( 45, 73), ( -1, 78) ]],
            chess.PAWN:
            [[ ],
            [ (  2, -8), (  4, -6), ( 11,  9), ( 18,  5), ( 16, 16), ( 21,  6), (  9, -6), ( -3,-18) ],
            [ ( -9, -9), (-15, -7), ( 11,-10), ( 15,  5), ( 31,  2), ( 23,  3), (  6, -8), (-20, -5) ],
            [ ( -3,  7), (-20,  1), (  8, -8), ( 19, -2), ( 39,-14), ( 17,-13), (  2,-11), ( -5, -6) ],
            [ ( 11, 12), ( -4,  6), (-11,  2), (  2, -6), ( 11, -5), (  0, -4), (-12, 14), (  5,  9) ],
            [ (  3, 27), (-11, 18), ( -6, 19), ( 22, 29), ( -8, 30), ( -5,  9), (-14,  8), (-11, 14) ],
            [ ( -7, -1), (  6,-14), ( -2, 13), (-11, 22), (  4, 24), (-14, 17), ( 10,  7), ( -9,  7) ],
            [ ]],
                }


    def getPST(self,piece, square, white):
        # Returns the piece square table tuple for the given piece, square and color.
        if not white: square = chess.square_mirror(square)
        if piece == chess.PAWN:
            mg,eg = self.pst[piece][square // 8][square % 8]
        else:
            mg,eg = self.pst[piece][square//8][min(square%8,7-square%8)]
        return (mg,eg)
    
    def getMGScore(self,board):
        # Returns the middle game score for the given board.
        pieceMap = board.piece_map()
        mgScore = {chess.WHITE:{}, chess.BLACK:{}}
        for square,piece in pieceMap.items():
            mgScore[piece.color][piece] = mgScore[piece.color].get(piece,0) + self.getPST(piece.piece_type, square, piece.color)[0]
        for color in [chess.WHITE, chess.BLACK]:
            mgScore[color]['total'] = sum(mgScore[color].values())
        return mgScore

    def getEGScore(self,board):
        # Returns the end game score for the given board.
        pieceMap = board.piece_map()
        egScore = {chess.WHITE:{}, chess.BLACK:{}}
        for square,piece in pieceMap.items():
            egScore[piece.color][piece] = egScore[piece.color].get(piece,0) + self.getPST(piece.piece_type, square, piece.color)[1]
        for color in [chess.WHITE, chess.BLACK]:
            egScore[color]['total'] = sum(egScore[color].values())
        return egScore
    
    def getNPawns(self,board,white):
        # Returns the number of pawns for the given color.
        return len(board.pieces(chess.PAWN,white))
    
    def getScore(self,board):
        # Returns the total score for the given board.
        mgScore = self.getMGScore(board)
        egScore = self.getEGScore(board)
        score = {chess.WHITE:{}, chess.BLACK:{}}
        for color in [chess.WHITE, chess.BLACK]:
           for piece in [chess.Piece(chess.PAWN,color),chess.Piece(chess.KNIGHT,color),chess.Piece(chess.BISHOP,color),chess.Piece(chess.ROOK,color),chess.Piece(chess.QUEEN,color),chess.Piece(chess.KING,color)]:
                opponentNPawns = self.getNPawns(board,not color)
                score[color][piece] = ( opponentNPawns*mgScore[color].get(piece,0) + (8-opponentNPawns)*egScore[color].get(piece,0) )/8
                score[color]['total'] = sum(score[color].values())
        return score
    
    def getScoreDiff(self,board):
        # Returns the difference in total score between the two colors.
        score = self.getScore(board)
        scoreDiff={}
        for piece in [chess.PAWN,chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN,chess.KING,chess.WHITE]:
            scoreDiff[piece] = score[chess.WHITE][chess.Piece(piece,chess.WHITE)] - score[chess.BLACK][chess.Piece(piece,chess.BLACK)]
        scoreDiff['total'] = sum(scoreDiff.values())
        return scoreDiff

    def plotScore(self,board):
        scoreDiff = self.getScoreDiff(board)
        stockfishScore = self.getStockfishScore(board)

        labels=['Pawns','Knights','Bishops','Rooks','Queen','King','Piece \n Placement','Stockfish']
        colors = ['C0','C1','C2','C3','C4','C5','k','C6']
        with plt.xkcd():
            plt.figure(figsize=(8,6))
            plt.axhline(y=0, color='gray', linestyle='-')
            bar=plt.bar(labels, [scoreDiff[chess.PAWN],scoreDiff[chess.KNIGHT],scoreDiff[chess.BISHOP],scoreDiff[chess.ROOK],scoreDiff[chess.QUEEN],scoreDiff[chess.KING],scoreDiff['total'],stockfishScore],color=colors)
            plt.bar_label(bar)
            plt.title('the fish says you should play '+self.getStockfishBestMove(board))
            plt.tight_layout()
            ymax=abs(max(plt.ylim(),key=abs))+10
            plt.ylim(-ymax,ymax)
            plt.ylabel('Centipawns')
            plt.show()
    def initStockfish(self):
        self.stockfish = Stockfish(path='./stockfish/stockfish-ubuntu-x86-64',
                              depth=6)
        
    def getStockfishScore(self,board):
        self.stockfish.set_fen_position(board.fen())
        return self.stockfish.get_evaluation()['value']
        
    def getStockfishBestMove(self,board):
        self.stockfish.set_fen_position(board.fen())
        return self.stockfish.get_best_move()

pstAnalyzer = PSTAnalyzerPosition()



# %%
        
with open('./game.pgn') as pgn:
    game = chess.pgn.read_game(pgn)
board=game.board()
pstAnalyzer = PSTAnalyzerPosition()
count=1
for move in game.mainline_moves():
    print(pstAnalyzer.getMGScore(board))
    print(pstAnalyzer.getEGScore(board))
    print(pstAnalyzer.getScore(board))
    print(pstAnalyzer.getScoreDiff(board))
    pstAnalyzer.plotScore(board)
    display(board)
    board.push(move)
    print('---------------------------------')

# %%

board=chess.Board('3rr3/ppq2pkp/2ppbnp1/4n3/P3P3/2N2N1P/1PPQBPP1/3R1RK1 w - - 0 1')
display(board)
pstAnalyzer.plotScore(board)

# %%

matplotlib.font_manager._rebuild()

# %%
