"""
Square value map.

Every square has a base value between 0.05 and 0.50.
Value increases:
  - The closer the square is to the center of the board
  - The closer the square is to the opponent's king

The final square value used during evaluation blends both:
    square_value(sq, board, color) = base_centrality(sq) + king_proximity_bonus(sq, board, color)
scaled so the total stays within [0.05, 0.50].
"""

import chess

# ── Static centrality map ────────────────────────────────────────────────────
# Pre-computed for all 64 squares.
# Center = e4/e5/d4/d5 → 0.50, corners → 0.05

def _build_centrality() -> dict[int, float]:
    """
    Distance from center is measured as Chebyshev distance to the
    nearest of the four central squares (d4=27, d5=35, e4=28, e5=36).
    Max Chebyshev distance from a corner to the nearest center square = 3.
    We map distance 0 → 0.50, distance 3 → 0.15, then clamp to [0.05, 0.50].
    """
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    table = {}
    for sq in chess.SQUARES:
        sq_file = chess.square_file(sq)
        sq_rank = chess.square_rank(sq)
        min_dist = min(
            max(abs(sq_file - chess.square_file(c)),
                abs(sq_rank - chess.square_rank(c)))
            for c in center_squares
        )
        # Linear interpolation: dist 0 → 0.50, dist 3 → 0.15
        value = 0.50 - min_dist * (0.50 - 0.15) / 3
        table[sq] = round(max(0.05, min(0.50, value)), 4)
    return table

CENTRALITY: dict[int, float] = _build_centrality()


# ── Dynamic king proximity bonus ─────────────────────────────────────────────

def _king_proximity_bonus(sq: int, king_sq: int) -> float:
    """
    Returns a bonus in [0.0, 0.15] based on Chebyshev distance
    from sq to the opponent's king.
    Distance 0 → 0.15, distance 7 → 0.00.
    """
    dist = chess.square_distance(sq, king_sq)
    bonus = 0.15 * (1 - dist / 7)
    return round(max(0.0, bonus), 4)


def square_value(sq: int, board: chess.Board, color: chess.Color) -> float:
    """
    Return the value of a square for the given color, blending
    static centrality and proximity to the opponent's king.
    The result is clamped to [0.05, 0.50].
    """
    opponent_color = not color
    king_sq = board.king(opponent_color)

    base = CENTRALITY[sq]
    bonus = _king_proximity_bonus(sq, king_sq) if king_sq is not None else 0.0

    return round(min(0.50, max(0.05, base + bonus)), 4)
