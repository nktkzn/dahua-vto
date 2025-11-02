import os
from pathlib import Path

# Path to the shared session file (next to scripts)
SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.txt")


def _read_session_from_file(path: str) -> str | None:
    """Return trimmed session id from file or None if missing/empty."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            sid = f.read().strip()
            return sid or None
    except FileNotFoundError:
        return None
    except OSError as e:
        print(f"Warning: cannot read session file '{path}': {e}")
        return None


def _save_session_to_file(path: str, session_id: str) -> None:
    """Persist a session id to file (overwrites)."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(session_id.strip() + "\n")
        print(f"Saved session id to '{path}'.")
    except OSError as e:
        print(f"Warning: cannot write session file '{path}': {e}")


def _prompt_yes_no(question: str, default: bool = True) -> bool:
    """Simple [Y/n] / [y/N] prompt."""
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        ans = input(f"{question} {suffix} ").strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes", "д", "да"):
            return True
        if ans in ("n", "no", "н", "нет"):
            return False
        print("Please answer with 'y' or 'n' / Ответьте 'y' или 'n'.")


def ensure_session(interactive: bool = True) -> str:
    """
    Ensure a Dahua RPC session id is available.

    1) If SESSION_FILE exists and contains an id, return it.
    2) If not and interactive=True:
       - Prompt the user:
         RU: 'Сначала запустить get_id.py? Или ввести ID вручную?'
         EN: 'Run get_id.py first? Or enter session id manually?'
       - If user chooses manual entry, save it to SESSION_FILE and return it.
       - Otherwise raise RuntimeError with a hint to run get_id.py.
    3) If not interactive, raise RuntimeError.
    """
    existing = _read_session_from_file(SESSION_FILE)
    if existing:
        return existing

    if not interactive:
        raise RuntimeError("No session found. Run get_id.py first to create 'session.txt'.")

    print("No 'session.txt' found or it's empty.")
    print("RU: Сначала запустите get_id.py, чтобы получить сессию.")
    print("EN: Please run get_id.py first to obtain a session id.")
    if _prompt_yes_no("Would you like to enter a session id manually now? / Ввести ID вручную сейчас?", default=True):
        sid = input("Enter session id / Введите session id: ").strip()
        if not sid:
            raise RuntimeError("Empty session id. Aborting.")
        _save_session_to_file(SESSION_FILE, sid)
        return sid
    raise RuntimeError("No session id provided. Run get_id.py to create one.")

# Convenience alias
load_session = ensure_session


if __name__ == "__main__":
    # CLI usage: print the session id (prompt if needed)
    try:
        sid = ensure_session(interactive=True)
        print("Session id:", sid)
        print(f"Stored at: {SESSION_FILE}")
    except RuntimeError as e:
        print(f"Error: {e}")
