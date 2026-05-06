"""
Transposition Table.

Stores search results keyed by Zobrist hash of the board position.
Each entry records:
  - score  : the evaluated score at this node
  - depth  : how deep the search was when this was stored
  - flag   : EXACT | LOWERBOUND | UPPERBOUND (for alpha-beta correctness)
  - move   : best move found (used for move ordering on TT hits)
"""

import chess

EXACT      = 0
LOWERBOUND = 1
UPPERBOUND = 2

MAX_TABLE_SIZE = 1_000_000  # entries — ~100 MB upper bound


class TTEntry:
    __slots__ = ("score", "depth", "flag", "move")

    def __init__(self, score: float, depth: int, flag: int, move: chess.Move | None):
        self.score = score
        self.depth = depth
        self.flag  = flag
        self.move  = move


class TranspositionTable:
    def __init__(self):
        self._table: dict[int, TTEntry] = {}

    def get(self, board: chess.Board, depth: int, alpha: float, beta: float):
        """
        Look up the current position.
        Returns (score, best_move) if the entry is usable, else (None, None).
        """
        entry = self._table.get(board._transposition_key())
        if entry is None or entry.depth < depth:
            best_move = entry.move if entry else None
            return None, best_move

        score = entry.score
        if entry.flag == EXACT:
            return score, entry.move
        if entry.flag == LOWERBOUND and score >= beta:
            return score, entry.move
        if entry.flag == UPPERBOUND and score <= alpha:
            return score, entry.move

        return None, entry.move  # entry exists but not usable for cutoff

    def store(self, board: chess.Board, score: float, depth: int,
              flag: int, move: chess.Move | None):
        """Store a result. Overwrites if new entry is deeper."""
        key = board._transposition_key()
        existing = self._table.get(key)
        if existing is None or depth >= existing.depth:
            if len(self._table) >= MAX_TABLE_SIZE:
                # Simple replacement: clear oldest 10 % when full
                keys = list(self._table.keys())
                for k in keys[:MAX_TABLE_SIZE // 10]:
                    del self._table[k]
            self._table[key] = TTEntry(score, depth, flag, move)

    def clear(self):
        self._table.clear()
