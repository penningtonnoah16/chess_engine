"""
Piece values used throughout the engine.
"""

import chess

PIECE_VALUES = {
    chess.PAWN:   1.00,
    chess.KNIGHT: 2.95,
    chess.BISHOP: 3.10,
    chess.ROOK:   5.00,
    chess.QUEEN:  10.00,
    chess.KING:   0.00,  # King has no material value in evaluation
}
