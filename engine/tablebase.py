"""
Tablebase probe for positions with 7 pieces or fewer.
Uses the Syzygy tablebase via the Lichess online API (no local files needed).
Returns the best move in UCI format, or None if not applicable.
"""

import requests
import chess

TABLEBASE_API = "https://tablebase.lichess.ovh/standard"


def probe_tablebase(board: chess.Board) -> str | None:
    """
    Query the Lichess Syzygy tablebase for the given position.
    Returns the best move in UCI format, or None if the position
    has more than 7 pieces or the query fails.
    """
    if bin(board.occupied).count("1") > 7:
        return None

    fen = board.fen()
    try:
        r = requests.get(TABLEBASE_API, params={"fen": fen}, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[Tablebase] Query failed: {e}")
        return None

    moves = data.get("moves")
    if not moves:
        return None

    # The API returns moves sorted by quality (best first).
    # Category priority: "win" > "unknown" > "draw" > "loss"
    best = moves[0]
    print(f"[Tablebase] Best move: {best['uci']} (category: {best['category']})")
    return best["uci"]
