"""
Main engine interface.
Decides which layer handles the current position:
  1. Opening book  (if still in known theory)
  2. Tablebase     (if 7 pieces or fewer on the board)
  3. Minimax search (everything else)
"""

import chess
from engine.opening_book import get_book_move
from engine.tablebase import probe_tablebase
from engine.search import find_best_move


class Engine:
    def choose_move(self, board: chess.Board, moves_played: list[str]) -> str | None:
        """
        Return the best move in UCI format for the given position.

        Parameters
        ----------
        board        : current chess.Board state
        moves_played : list of all moves played so far in UCI format
        """

        # 1. Opening book
        book_move = get_book_move(moves_played)
        if book_move:
            return book_move

        # 2. Tablebase (endgame — 7 pieces or fewer)
        tb_move = probe_tablebase(board)
        if tb_move:
            return tb_move

        # 3. Minimax search
        move = find_best_move(board)
        return move.uci() if move else None
