from const import *
from square import Square
from piece import *
from move import Move

class Board:
    def __init__(self) -> None:
        self.squares = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        self.last_move = None

    def move(self, piece, move):
        initial = move.initial
        final = move.final

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # pawn promotion
        if isinstance(piece,Pawn):
            self.check_promotion(piece,final)

        #king castling
        if isinstance(piece,King):
            if self.castling(initial,final):
                diff = final.col - initial.col
                rook = piece.left_rook if (diff< 0) else piece.right_rook
                self.move(rook,rook.moves[-1])

        # move
        piece.moved = True
        # clear valid moves
        piece.clear_moves()
        # set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self,piece,final):
        if final.row==0 or final.row==7:
            self.squares[final.row][final.col].piece = Queen(piece.color)
    def castling(self,initial,final):
        return abs(initial.col - final.col) == 2

    def calc_moves(self, piece, row, col):
        def knight_moves():
            # 8 possible moves
            possible_moves = [
                (row - 2, col + 1),
                (row - 1, col + 2),
                (row + 1, col + 2),
                (row + 2, col + 1),
                (row + 2, col - 1),
                (row + 1, col - 2),
                (row - 1, col - 2),
                (row - 2, col - 1)
            ]
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_opp(piece.color):
                        # squares for the new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # new move
                        move = Move(initial, final)
                        # append new valid move
                        piece.add_move(move)

        def pawn_moves():
            steps = 1 if piece.moved else 2
            
            # vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].is_empty():
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        # create a new move
                        move = Move(initial, final)
                        piece.add_move(move)
                    # blocked
                    else:
                        break
                # not in range
                else:
                    break

            # diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col - 1, col + 1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_opp_piece(piece.color):
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # create a new move
                        move = Move(initial, final)
                        piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                possible_move_row = row + incr[0]
                possible_move_col = col + incr[1]
                while Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_opp(piece.color):
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # create a new move
                        move = Move(initial, final)
                        piece.add_move(move)
                        # if it has opponent piece, break
                        if self.squares[possible_move_row][possible_move_col].has_opp_piece(piece.color):
                            break
                    else:
                        break
                    possible_move_row += incr[0]
                    possible_move_col += incr[1]

        def bishop_moves():
            straightline_moves([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        def rook_moves():
            straightline_moves([(-1, 0), (1, 0), (0, -1), (0, 1)])

        def queen_moves():
            straightline_moves([(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])

        def king_moves():
            possible_moves = [
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1),
                (row - 1, col - 1),
                (row - 1, col + 1),
                (row + 1, col - 1),
                (row + 1, col + 1)
            ]
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_opp(piece.color):
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial, final)
                        piece.add_move(move)
            # castling moves
            if not piece.moved:
                # Queenside castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook) and not left_rook.moved:
                    if all(self.squares[row][col].is_empty() for col in range(1, 4)):
                        # Add left rook to king
                        piece.left_rook = left_rook
                        # Rook move
                        initial = Square(row, 0)
                        final = Square(row, 3)
                        move = Move(initial, final)
                        left_rook.add_move(move)
                        # King move
                        initial = Square(row, col)
                        final = Square(row, 2)
                        move = Move(initial, final)
                        piece.add_move(move)
                # Kingside castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook) and not right_rook.moved:
                    if all(self.squares[row][col].is_empty() for col in range(5, 7)):
                        # Add right rook to king
                        piece.right_rook = right_rook
                        # Rook move
                        initial = Square(row, 7)
                        final = Square(row, 5)
                        move = Move(initial, final)
                        right_rook.add_move(move)
                        # King move
                        initial = Square(row, col)
                        final = Square(row, 6)
                        move = Move(initial, final)
                        piece.add_move(move)



        if isinstance(piece, Pawn):
            pawn_moves()

        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Bishop):
            bishop_moves()

        elif isinstance(piece, Rook):
            rook_moves()

        elif isinstance(piece, Queen):
            queen_moves()

        elif isinstance(piece, King):
            king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col].piece = Pawn(color)
        # knights
        self.squares[row_other][1].piece = Knight(color)
        self.squares[row_other][6].piece = Knight(color)
        # bishops
        self.squares[row_other][2].piece = Bishop(color)
        self.squares[row_other][5].piece = Bishop(color)
        # rooks
        self.squares[row_other][0].piece = Rook(color)
        self.squares[row_other][7].piece = Rook(color)
        # King and Queen
        self.squares[row_other][4].piece = King(color)
        self.squares[row_other][3].piece = Queen(color)
    def restart_board(self):
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        self.last_move = None