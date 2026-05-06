"""
Chess Engine - Entry Point
"""

from bot.lichess_client import LichessClient


def main():
    client = LichessClient()
    client.run()


if __name__ == "__main__":
    main()
