"""
Position evaluator.

Provides a single absolute evaluation of a board position from a given
color's perspective. This is the leaf-node score used by the search.

Score = material balance + positional balance (controlled square values).

Using an absolute evaluation at every leaf — rather than accumulating
move-by-move deltas — eliminates the perspective mismatch that caused
phantom capture scores in the previous architecture.
"""

import chess
from engine.piece_values import PIECE_VALUES
from engine.square_values import square_value


def _controlled_value(sq: int, board: chess.Board, color: chess.Color) -> float:
    """Sum of square_value() for every square the piece on `sq` attacks."""
    return sum(
        square_value(attacked_sq, board, color)
        for attacked_sq in board.attacks(sq)
    )


def position_eval(board: chess.Board, color: chess.Color) -> float:
    """
    Evaluate the board from `color`'s perspective.
    Higher = better for `color`.

    Components
    ----------
    1. Material balance  — piece values as defined in piece_values.py
    2. Positional balance — sum of controlled square values for every piece
       on the board (own pieces add, opponent pieces subtract).
       Square values range [0.05, 0.50] so this component naturally stays
       on the same scale as the pawn (1.0), rewarding control without
       overshadowing material.
    """
    score = 0.0

    # ── Material ─────────────────────────────────────────────────────────────
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, color))       * value
        score -= len(board.pieces(piece_type, not color))   * value

    # ── Positional (controlled squares) ──────────────────────────────────────
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        ctrl = _controlled_value(sq, board, piece.color)
        if piece.color == color:
            score += ctrl
        else:
            score -= ctrl

    return score
