"""
Opening book based on human opening theory.

Structure
---------
Each entry maps a position (identified by the full move history as a tuple
of UCI strings) to a LIST of acceptable book moves. When multiple moves are
listed, one is chosen at random — this prevents the engine from playing the
exact same game every time.

Openings included
-----------------
AS WHITE
  • Ruy López  (Spanish Opening)  — via 1.e4
  • Queen's Gambit                — via 1.d4

AS BLACK
  • vs 1.e4  → 1...e5 (normal response, heading for Spanish or Italian)
  • vs 1.d4 2.c4 → Queen's Gambit Declined (1...d5 2...e6)
"""

import random

# ---------------------------------------------------------------------------
# Type alias: position key → list of candidate moves (UCI strings)
# ---------------------------------------------------------------------------
OPENING_BOOK: dict[tuple, list[str]] = {

    # ════════════════════════════════════════════════════════════════════════
    # WHITE — MOVE 1: randomly play e4 (Ruy López path) or d4 (QG path)
    # ════════════════════════════════════════════════════════════════════════
    (): ["e2e4", "d2d4"],


    # ════════════════════════════════════════════════════════════════════════
    # WHITE — RUY LÓPEZ  (1.e4 e5 2.Nf3 Nc6 3.Bb5)
    # ════════════════════════════════════════════════════════════════════════

    # 1...e5 → 2.Nf3
    ("e2e4", "e7e5"):                                               ["g1f3"],
    # 2...Nc6 → 3.Bb5  (the López move)
    ("e2e4", "e7e5", "g1f3", "b8c6"):                              ["f1b5"],
    # 2...Nf6 (Petrov) → 3.Nxe5
    ("e2e4", "e7e5", "g1f3", "g8f6"):                              ["f3e5"],

    # ── 3...a6  Morphy Defence ───────────────────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6"):             ["b5a4"],
    # 4...Nf6 → 5.O-O
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6"):                                               ["e1g1"],
    # 5...Be7 → 6.Re1  Closed Ruy López
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "f8e7"):                              ["f1e1"],
    # 5...b5 → 6.Bb3
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "b7b5"):                              ["a4b3"],
    # 6...Be7 → 7.Bb3
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "f8e7", "f1e1", "b7b5"):             ["a4b3"],
    # 7...d6 → 8.c3
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "f8e7", "f1e1", "b7b5",
     "a4b3", "d7d6"):                                               ["c2c3"],
    # 7...O-O → 8.c3
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "f8e7", "f1e1", "b7b5",
     "a4b3", "e8g8"):                                               ["c2c3"],

    # ── 3...Nf6  Berlin Defence ──────────────────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6"):             ["e1g1"],
    # 4...Nxe4 → 5.d4
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6",
     "e1g1", "f6e4"):                                               ["d2d4"],

    # ── 3...d6  Steinitz Defence → 4.c3 ─────────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "d7d6"):             ["c2c3"],

    # ── 3...f5  Schliemann-Jaenisch → 4.Nc3 ─────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "f7f5"):             ["b1c3"],

    # ── 3...Bc5  Classical / Cordel → 4.c3 ──────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "f8c5"):             ["c2c3"],

    # ── 3...Nge7  Cozio → 4.c3 ──────────────────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8e7"):             ["c2c3"],

    # ── 3...g6  Smyslov → 4.c3 ──────────────────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g7g6"):             ["c2c3"],


    # ════════════════════════════════════════════════════════════════════════
    # WHITE — QUEEN'S GAMBIT  (1.d4 d5 2.c4)
    # ════════════════════════════════════════════════════════════════════════

    # 1...d5 → 2.c4  (the gambit)
    ("d2d4", "d7d5"):                                               ["c2c4"],
    # 1...Nf6 → 2.c4
    ("d2d4", "g8f6"):                                               ["c2c4"],
    # 1...e6 → 2.c4
    ("d2d4", "e7e6"):                                               ["c2c4"],
    # 1...f5 (Dutch) → 2.c4
    ("d2d4", "f7f5"):                                               ["c2c4"],

    # 2...e6  QGD → 3.Nc3
    ("d2d4", "d7d5", "c2c4", "e7e6"):                              ["b1c3"],
    # 2...c6  Slav → 3.Nc3
    ("d2d4", "d7d5", "c2c4", "c7c6"):                              ["b1c3"],
    # 2...dxc4  QGA → 3.e3
    ("d2d4", "d7d5", "c2c4", "d5c4"):                              ["e2e3"],
    # 2...Nf6  → 3.Nc3
    ("d2d4", "d7d5", "c2c4", "g8f6"):                              ["b1c3"],
    # 2...e5  (Albin Counter-Gambit) → 3.dxe5
    ("d2d4", "d7d5", "c2c4", "e7e5"):                              ["d4e5"],
    # 2...c5  (Symmetrical) → 3.cxd5
    ("d2d4", "d7d5", "c2c4", "c7c5"):                              ["c4d5"],

    # After 3.Nc3 vs QGD: 3...Nf6 → 4.Bg5
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6"):             ["c1g5"],
    # 4...Be7 → 5.e3
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
     "c1g5", "f8e7"):                                               ["e2e3"],
    # 4...Nbd7 → 5.e3
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
     "c1g5", "b8d7"):                                               ["e2e3"],
    # 5...O-O → 6.Nf3
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
     "c1g5", "f8e7", "e2e3", "e8g8"):                              ["g1f3"],

    # After 3.Nc3 vs Slav: 3...Nf6 → 4.Nf3
    ("d2d4", "d7d5", "c2c4", "c7c6", "b1c3", "g8f6"):             ["g1f3"],
    # 4...dxc4 → 5.a4
    ("d2d4", "d7d5", "c2c4", "c7c6", "b1c3", "g8f6",
     "g1f3", "d5c4"):                                               ["a2a4"],
    # 4...e6 → 5.e3
    ("d2d4", "d7d5", "c2c4", "c7c6", "b1c3", "g8f6",
     "g1f3", "e7e6"):                                               ["e2e3"],


    # ════════════════════════════════════════════════════════════════════════
    # BLACK — vs 1.e4  →  normal response 1...e5
    # (preparing for Spanish or Italian)
    # ════════════════════════════════════════════════════════════════════════

    # 1.e4 → e5
    ("e2e4",):                                                      ["e7e5"],

    # 2.Nf3 → Nc6
    ("e2e4", "e7e5", "g1f3"):                                      ["b8c6"],

    # ── vs Ruy López  3.Bb5 ─────────────────────────────────────────────
    # → randomly play Morphy (a6) or Berlin (Nf6)
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5"):                     ["a7a6", "g8f6"],

    # Morphy: 4.Ba4 → Nf6
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5a4"):    ["g8f6"],
    # 5.O-O → Be7
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1"):                                       ["f8e7"],
    # 6.Re1 → b5
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "f8e7", "f1e1"):                     ["b7b5"],
    # 7.Bb3 → d6  (Closed Ruy López main line)
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "f8e7", "f1e1", "b7b5", "a4b3"):    ["d7d6"],
    # 8.c3 → O-O
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
     "b5a4", "g8f6", "e1g1", "f8e7", "f1e1", "b7b5",
     "a4b3", "d7d6", "c2c3"):                                       ["e8g8"],

    # Berlin: 4.O-O → Nxe4
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6", "e1g1"):    ["f6e4"],
    # 5.d4 → Nd6
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6",
     "e1g1", "f6e4", "d2d4"):                                       ["f6d5"],

    # ── vs Italian  3.Bc4 ───────────────────────────────────────────────
    # → randomly play Bc5 (Giuoco Piano) or Nf6 (Two Knights)
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4"):                     ["f8c5", "g8f6"],

    # Giuoco Piano: 4.c3 → Nf6
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "c2c3"):    ["g8f6"],
    # 4.d3 → Nf6
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "d2d3"):    ["g8f6"],

    # Two Knights: 4.Ng5 → d5
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "g1g5"):    ["d7d5"],
    # 4.d3 → Bc5
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "d2d3"):    ["f8c5"],
    # 4.O-O → Bc5
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "e1g1"):    ["f8c5"],

    # ── vs Scotch  3.d4 ─────────────────────────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "d2d4"):                     ["e5d4"],

    # ── vs Four Knights  3.Nc3 ──────────────────────────────────────────
    ("e2e4", "e7e5", "g1f3", "b8c6", "b1c3"):                     ["g8f6"],

    # ── vs King's Gambit  2.f4 ──────────────────────────────────────────
    ("e2e4", "e7e5", "f2f4"):                                      ["e5f4", "d7d5"],


    # ════════════════════════════════════════════════════════════════════════
    # BLACK — vs 1.d4  →  Queen's Gambit Declined
    # ════════════════════════════════════════════════════════════════════════

    # 1.d4 → d5
    ("d2d4",):                                                      ["d7d5"],

    # 2.c4 → e6  (QGD)
    ("d2d4", "d7d5", "c2c4"):                                      ["e7e6"],

    # 3.Nc3 → Nf6
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3"):                     ["g8f6"],
    # 3.Nf3 → Nf6
    ("d2d4", "d7d5", "c2c4", "e7e6", "g1f3"):                     ["g8f6"],

    # 4.Bg5 → Be7  (Orthodox QGD)
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c1g5"):    ["f8e7"],
    # 4.Nf3 → Be7
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "g1f3"):    ["f8e7"],
    # 4.e3 → Be7
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "e2e3"):    ["f8e7"],

    # 5.e3 → O-O
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
     "c1g5", "f8e7", "e2e3"):                                       ["e8g8"],
    # 5.Nf3 → O-O
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
     "c1g5", "f8e7", "g1f3"):                                       ["e8g8"],

    # 6.Nf3 → h6 (to challenge the pin) or Nbd7
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
     "c1g5", "f8e7", "e2e3", "e8g8", "g1f3"):                     ["h7h6", "b8d7"],

    # vs 2.Nf3 (no gambit) → Nf6
    ("d2d4", "d7d5", "g1f3"):                                      ["g8f6"],
    # vs 2.e3 → Nf6
    ("d2d4", "d7d5", "e2e3"):                                      ["g8f6"],
    # vs 2.Bf4 → c5
    ("d2d4", "d7d5", "c1f4"):                                      ["c7c5"],
}


def get_book_move(moves: list[str]) -> str | None:
    """
    Given the list of moves played so far (in UCI format),
    return a book move chosen at random from the candidates,
    or None if the position is out of book.
    """
    key       = tuple(moves)
    candidates = OPENING_BOOK.get(key)
    if not candidates:
        return None
    move = random.choice(candidates)
    print(f"[Opening Book] Book move: {move}"
          + (f"  (chosen from {candidates})" if len(candidates) > 1 else ""))
    return move
