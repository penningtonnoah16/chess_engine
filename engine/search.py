"""
Search — Negamax + Alpha-Beta + MVV-LVA Move Ordering
         + Quiescence Search + Transposition Table
         + Iterative Deepening with time and early-exit controls.

Architecture
------------
All scores are always from the perspective of `board.turn` at that node.
Recursion negates the score and flips alpha/beta windows (negamax).
This makes quiescence and the main search fully consistent — no more
perspective mismatches that caused phantom +10 scores.

Time control
------------
  Hard limit : 120 seconds (2 minutes)
  Early exit : depth >= 12, gain >= +5.0 over the starting position,
               AND quiescence confirms the resulting position is quiet.
"""

import time
import chess

from engine.evaluator import position_eval
from engine.piece_values import PIECE_VALUES
from engine.transposition_table import TranspositionTable, EXACT, LOWERBOUND, UPPERBOUND

# ── Constants ────────────────────────────────────────────────────────────────

TIME_LIMIT       = 120.0   # seconds
EARLY_EXIT_GAIN  = 5.0     # gain over starting eval to trigger early exit
EARLY_EXIT_DEPTH = 12      # minimum depth before early exit is considered
QUIET_TOLERANCE  = 0.25    # quiescence must agree within this margin
INF              = float("inf")
MATE_SCORE       = 1_000.0

# ── Global search state (reset each move) ────────────────────────────────────

_tt            = TranspositionTable()
_start_time    = 0.0
_time_exceeded = False


def _out_of_time() -> bool:
    return time.time() - _start_time >= TIME_LIMIT


# ── Move Ordering ─────────────────────────────────────────────────────────────

def _mvv_lva_score(move: chess.Move, board: chess.Board) -> float:
    """
    MVV-LVA: Most Valuable Victim — Least Valuable Attacker.
    Winning captures (low attacker takes high victim) score highest.
    Losing captures (queen takes pawn) score lowest among captures.
    """
    victim = board.piece_at(move.to_square)
    if victim is None:
        return 0.0
    attacker  = board.piece_at(move.from_square)
    v_val     = PIECE_VALUES.get(victim.piece_type,   0.0)
    a_val     = PIECE_VALUES.get(attacker.piece_type, 0.0) if attacker else 0.0
    return v_val * 10.0 - a_val


def _order_moves(
    moves: list[chess.Move],
    board: chess.Board,
    tt_move: chess.Move | None,
) -> list[chess.Move]:
    """
    Priority order:
      1. TT move from previous iteration (almost always causes a cut)
      2. Winning / equal captures, sorted by MVV-LVA
      3. Quiet moves
      4. Losing captures (e.g. queen takes protected pawn)
    """
    def key(m: chess.Move) -> float:
        if m == tt_move:
            return 2_000.0
        s = _mvv_lva_score(m, board)
        if s > 0:
            return s        # captures: range ~ 0.05 – 99
        return -1.0         # quiet moves

    return sorted(moves, key=key, reverse=True)


# ── Quiescence Search ─────────────────────────────────────────────────────────

def quiescence(board: chess.Board, alpha: float, beta: float) -> float:
    """
    Negamax quiescence: extend search on captures only until quiet.
    Score is always from `board.turn`'s perspective.

    Stand-pat: the side to move may choose not to capture
    (assume the position is already fine without further captures).
    """
    stand_pat = position_eval(board, board.turn)

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    for move in board.generate_pseudo_legal_captures():
        if not board.is_legal(move):
            continue
        board.push(move)
        score = -quiescence(board, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


# ── Negamax with Alpha-Beta ───────────────────────────────────────────────────

def negamax(
    board: chess.Board,
    depth: int,
    alpha: float,
    beta: float,
) -> float:
    """
    Negamax alpha-beta with transposition table.
    Returns the score of the position from `board.turn`'s perspective.
    """
    global _time_exceeded

    if _out_of_time():
        _time_exceeded = True
        return 0.0

    # ── TT lookup ────────────────────────────────────────────────────────────
    tt_score, tt_move = _tt.get(board, depth, alpha, beta)
    if tt_score is not None:
        return tt_score

    # ── Terminal / leaf nodes ─────────────────────────────────────────────────
    if board.is_game_over():
        if board.is_checkmate():
            return -MATE_SCORE  # board.turn is checkmated
        return 0.0              # stalemate / draw

    if depth == 0:
        return quiescence(board, alpha, beta)

    # ── Recurse ───────────────────────────────────────────────────────────────
    legal_moves    = list(board.legal_moves)
    ordered        = _order_moves(legal_moves, board, tt_move)
    original_alpha = alpha
    best_score     = -INF
    best_move      = None

    for move in ordered:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        if _time_exceeded:
            return best_score if best_move else 0.0

        if score > best_score:
            best_score = score
            best_move  = move

        alpha = max(alpha, best_score)
        if alpha >= beta:
            break  # Beta cut-off

    # ── Store in TT ───────────────────────────────────────────────────────────
    if best_score <= original_alpha:
        flag = UPPERBOUND
    elif best_score >= beta:
        flag = LOWERBOUND
    else:
        flag = EXACT

    _tt.store(board, best_score, depth, flag, best_move)
    return best_score


# ── Iterative Deepening ───────────────────────────────────────────────────────

def find_best_move(board: chess.Board) -> chess.Move | None:
    """
    Iterative deepening driver.

    Searches depth 1 → 2 → 3 … until:
      A) 120 seconds elapsed                                (hard time limit)
      B) depth >= 12, gain over starting position >= +5.0,
         AND quiescence confirms position is quiet          (early exit)

    The gain is the improvement in absolute evaluation from the starting
    position, so +5.0 means the engine is objectively up a rook or more
    compared to where it started this move.

    Returns the best move found at the deepest fully completed depth.
    """
    global _start_time, _time_exceeded
    _start_time    = time.time()
    _time_exceeded = False
    _tt.clear()

    # Baseline: evaluation of the position BEFORE any move is made.
    # Used to compute the gain (flag) relative to the start.
    baseline = position_eval(board, board.turn)

    best_move  = None
    best_score = -INF
    depth      = 1

    while True:
        # ── Single depth iteration ────────────────────────────────────────
        iteration_best_move  = None
        iteration_best_score = -INF

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        _, tt_move = _tt.get(board, 0, -INF, INF)
        ordered    = _order_moves(legal_moves, board, tt_move or best_move)

        for move in ordered:
            if _out_of_time():
                _time_exceeded = True
                break

            board.push(move)
            # Negate because after push it is the opponent's turn
            score = -negamax(board, depth - 1, -INF, INF)
            board.pop()

            if score > iteration_best_score:
                iteration_best_score = score
                iteration_best_move  = move

        # Accept completed iteration
        if not _time_exceeded and iteration_best_move is not None:
            best_move  = iteration_best_move
            best_score = iteration_best_score
            gain       = best_score - baseline
            elapsed    = time.time() - _start_time
            print(
                f"[Search] depth={depth:>2}  "
                f"flag={gain:+.4f}  "
                f"move={best_move.uci()}  "
                f"elapsed={elapsed:.1f}s"
            )

        # ── Stop conditions ───────────────────────────────────────────────

        # A. Hard time limit
        if _out_of_time() or _time_exceeded:
            print(f"[Search] Time limit reached at depth {depth}.")
            break

        # B. Early exit: deep enough, large enough gain, quiet position
        if best_move and depth >= EARLY_EXIT_DEPTH:
            gain = best_score - baseline
            if gain >= EARLY_EXIT_GAIN:
                # Push the best move and run quiescence from the opponent's
                # perspective. If the resolved score (negated back to ours)
                # is close to best_score, no captures can unravel the gain.
                board.push(best_move)
                qs_from_opponent = quiescence(board, -INF, INF)
                board.pop()

                resolved = -qs_from_opponent  # back to engine's perspective
                quiet    = abs(resolved - best_score) <= QUIET_TOLERANCE

                if quiet:
                    print(
                        f"[Search] Early exit — gain {gain:+.4f} >= +5 "
                        f"at depth {depth}, position confirmed quiet."
                    )
                    break
                else:
                    print(
                        f"[Search] Gain >= +5 but position not quiet "
                        f"(resolved={resolved:+.4f} vs score={best_score:+.4f}), "
                        f"continuing..."
                    )

        depth += 1

    if best_move:
        gain = best_score - baseline
        print(f"[Search] Final — move={best_move.uci()}  flag={gain:+.4f}")
    return best_move
