"""
Lichess BOT API client.
Handles authentication, event streaming, and game loop.
"""

import os
import json
import threading
import requests
import chess

from dotenv import load_dotenv
from engine.engine import Engine

load_dotenv()

API_BASE = "https://lichess.org/api"


class LichessClient:
    def __init__(self):
        self.token = os.getenv("LICHESS_TOKEN")
        if not self.token:
            raise ValueError("LICHESS_TOKEN not set in .env file.")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.engine   = Engine()
        self.username = None

    def get_profile(self):
        """Fetch and return the bot's own profile."""
        r = requests.get(f"{API_BASE}/account", headers=self.headers)
        r.raise_for_status()
        return r.json()

    def stream_events(self):
        """Stream incoming events (challenges, game starts, etc.)."""
        with requests.get(
            f"{API_BASE}/stream/event",
            headers=self.headers,
            stream=True,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    yield json.loads(line)

    def accept_challenge(self, challenge_id: str):
        """Accept an incoming challenge."""
        r = requests.post(
            f"{API_BASE}/challenge/{challenge_id}/accept",
            headers=self.headers,
        )
        r.raise_for_status()

    def decline_challenge(self, challenge_id: str):
        """Decline an incoming challenge."""
        r = requests.post(
            f"{API_BASE}/challenge/{challenge_id}/decline",
            headers=self.headers,
        )
        r.raise_for_status()

    def make_move(self, game_id: str, move: str):
        """Send a move in UCI format (e.g. 'e2e4')."""
        r = requests.post(
            f"{API_BASE}/bot/game/{game_id}/move/{move}",
            headers=self.headers,
        )
        r.raise_for_status()

    def stream_game(self, game_id: str):
        """Stream the state of a game."""
        with requests.get(
            f"{API_BASE}/bot/game/stream/{game_id}",
            headers=self.headers,
            stream=True,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    yield json.loads(line)

    # ── Game handler ─────────────────────────────────────────────────────────

    def _handle_game(self, game_id: str, bot_color: chess.Color):
        """
        Stream a game and respond with moves.
        Runs in its own thread so multiple games can be handled simultaneously.
        """
        print(f"[Game {game_id}] Starting — playing as {'White' if bot_color == chess.WHITE else 'Black'}")
        board        = chess.Board()
        moves_played = []

        for event in self.stream_game(game_id):
            event_type = event.get("type")

            # gameFull is sent once at the start with the complete game state
            if event_type == "gameFull":
                state = event.get("state", {})
                moves_uci = state.get("moves", "").split()
                self._sync_board(board, moves_uci)
                moves_played = moves_uci

            # gameState is sent on every move
            elif event_type == "gameState":
                moves_uci = event.get("moves", "").split()
                self._sync_board(board, moves_uci)
                moves_played = moves_uci

                status = event.get("status", "started")
                if status != "started":
                    print(f"[Game {game_id}] Game over — status: {status}")
                    return

            else:
                continue

            # Play a move only when it is the bot's turn
            if board.turn != bot_color:
                continue
            if board.is_game_over():
                return

            print(f"[Game {game_id}] Thinking... (move {board.fullmove_number})")
            move_uci = self.engine.choose_move(board, moves_played)

            if move_uci is None:
                print(f"[Game {game_id}] Engine returned no move — resigning.")
                requests.post(
                    f"{API_BASE}/bot/game/{game_id}/resign",
                    headers=self.headers,
                )
                return

            print(f"[Game {game_id}] Playing: {move_uci}")
            try:
                self.make_move(game_id, move_uci)
            except requests.HTTPError as e:
                print(f"[Game {game_id}] Move rejected by Lichess: {e}")
                return

    def _sync_board(self, board: chess.Board, moves_uci: list[str]):
        """Reset board and replay all moves from the move list."""
        board.reset()
        for uci in moves_uci:
            try:
                board.push_uci(uci)
            except ValueError as e:
                print(f"[Sync] Illegal move in history '{uci}': {e}")
                break

    # ── Main event loop ───────────────────────────────────────────────────────

    def run(self):
        """Listen for events and dispatch game threads."""
        profile      = self.get_profile()
        self.username = profile["username"]
        print(f"Logged in as: {self.username}")

        for event in self.stream_events():
            event_type = event.get("type")

            if event_type == "challenge":
                challenge    = event["challenge"]
                challenge_id = challenge["id"]
                challenger   = challenge["challenger"]["name"]
                print(f"[Event] Challenge from {challenger} — accepting.")
                try:
                    self.accept_challenge(challenge_id)
                except requests.HTTPError as e:
                    print(f"[Event] Could not accept challenge: {e}")

            elif event_type == "gameStart":
                game      = event["game"]
                game_id   = game["id"]
                bot_color = chess.WHITE if game["color"] == "white" else chess.BLACK

                # Each game runs in its own thread
                t = threading.Thread(
                    target=self._handle_game,
                    args=(game_id, bot_color),
                    daemon=True,
                )
                t.start()
