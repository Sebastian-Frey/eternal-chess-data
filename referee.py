"""
Eternal Chess — Move Referee
Validates a SAN move against the current game state using python-chess,
then updates game_state.json with the new FEN and move history.
"""

import chess
import json
import sys
import os
from datetime import datetime, timezone


def load_state(path="game_state.json"):
    """Load the current game state from JSON."""
    with open(path, "r") as f:
        return json.load(f)


def save_state(state, path="game_state.json"):
    """Persist the updated game state back to JSON."""
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def determine_result(board):
    """Return the PGN result string for the current board position."""
    if board.is_checkmate():
        return "0-1" if board.turn == chess.WHITE else "1-0"
    if board.is_stalemate() or board.is_insufficient_material() or board.is_fifty_moves():
        return "1/2-1/2"
    return "*"


def main():
    move_san = os.environ.get("INPUT_MOVE")
    if not move_san:
        print("ERROR: No move provided (INPUT_MOVE is empty).")
        sys.exit(1)

    state = load_state()
    board = chess.Board(state["fen"])

    # Validate the move
    try:
        move = board.parse_san(move_san)
    except (chess.InvalidMoveError, chess.IllegalMoveError, chess.AmbiguousMoveError) as e:
        print(f"ILLEGAL MOVE: '{move_san}' — {e}")
        print(f"Current FEN: {board.fen()}")
        print(f"Legal moves: {', '.join(board.san(m) for m in board.legal_moves)}")
        sys.exit(1)

    # Apply the move
    board.push(move)
    print(f"VALID: {move_san}")
    print(f"New FEN: {board.fen()}")

    # Update state
    state["fen"] = board.fen()
    state["moves"].append(move_san)
    state["move_count"] += 1
    state["last_move"] = move_san
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["result"] = determine_result(board)

    if board.is_check():
        print("CHECK!")
    if board.is_checkmate():
        winner = "White" if board.turn == chess.BLACK else "Black"
        print(f"CHECKMATE — {winner} wins!")
    if board.is_stalemate():
        print("STALEMATE — Draw.")

    save_state(state)
    print(f"State saved. Total moves: {state['move_count']}")


if __name__ == "__main__":
    main()
