import os
import json
import hashlib
import requests
import getpass

"""
get_id.py — Login to Dahua DHI-VTO device and obtain a working session.

New features:
1) If a text file with credentials exists, the script asks whether to use it.
2) If the answer is No or the file is missing/incomplete, the script prompts
   for IP, username, and password, then writes them to the file.

Credentials file format (plain text, same directory):
    credentials.txt
    ----------------
    ip=192.168.1.10
    username=admin
    password=your_password

SECURITY NOTE: The password is stored in plaintext. Store this file securely.
"""

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.txt")
SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.txt")
DEFAULT_TIMEOUT = 5  # seconds


def _parse_kv_file(path: str) -> dict:
    """Parse simple key=value file into a lowercase-key dict."""
    creds = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                creds[k.strip().lower()] = v.strip()
    return creds


def _prompt_yes_no(question: str, default: bool = True) -> bool:
    """Simple [Y/n] / [y/N] prompt."""
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        ans = input(f"{question} {suffix} ").strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer with 'y' or 'n'.")


def _prompt_credentials(existing: dict | None = None) -> dict:
    """Ask user for IP, username, and password; show defaults if existing provided."""
    existing = existing or {}
    ip_default = existing.get("ip", "")
    user_default = existing.get("username", "")
    ip = input(f"Device IP{f' [{ip_default}]' if ip_default else ''}: ").strip() or ip_default
    username = input(f"Username{f' [{user_default}]' if user_default else ''}: ").strip() or user_default

    if existing.get("password"):
        pwd = getpass.getpass("Password (leave empty to keep the one from file): ")
        if pwd.strip() == "":
            pwd = existing["password"]
    else:
        pwd = getpass.getpass("Password: ")

    return {"ip": ip, "username": username, "password": pwd}


def _save_credentials(path: str, creds: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Plaintext credentials for Dahua device\n")
        f.write(f"ip={creds['ip']}\n")
        f.write(f"username={creds['username']}\n")
        f.write(f"password={creds['password']}\n")


def calculate_dahua_auth_hash(username: str, password: str, realm: str, random_key: str, encoding: str = "latin-1") -> str:
    """
    Computes the authentication hash using the double-MD5 method (UPPERCASE intermediate hash),
    matching the common JS implementations for Dahua devices.
    """
    print(f"--- Calculating hash with encoding: {encoding} ---")
    s1 = f"{username}:{realm}:{password}"
    h1_lower = hashlib.md5(s1.encode(encoding)).hexdigest()
    h1_upper = h1_lower.upper()
    print(f"String 1 (user:realm:pass): {s1}")
    print(f"Hash 1 (MD5 of string 1):   {h1_lower}")
    print(f"Hash 1 (in UPPERCASE):      {h1_upper}")
    print("-" * 40)

    s2 = f"{username}:{random_key}:{h1_upper}"
    final_hash_upper = hashlib.md5(s2.encode(encoding)).hexdigest().upper()
    print(f"String 2 (user:random:HASH1_UPPER): {s2}")
    print(f"Final hash (MD5 of string 2):       {final_hash_upper}")
    return final_hash_upper


def _get_credentials_interactive() -> dict:
    """Load from file (ask to use) or prompt and then save to file."""
    creds_from_file = None
    if os.path.exists(CREDENTIALS_FILE):
        try:
            parsed = _parse_kv_file(CREDENTIALS_FILE)
            # Only accept as "complete" if all needed keys are present
            if all(k in parsed for k in ("ip", "username", "password")):
                if _prompt_yes_no(f"Found '{os.path.basename(CREDENTIALS_FILE)}'. Use credentials from file?"):
                    return parsed
                else:
                    # Allow reusing existing values as defaults
                    creds_from_file = parsed
            else:
                print(f"Credentials file '{CREDENTIALS_FILE}' is incomplete. You'll be prompted to fill in the fields.")
                creds_from_file = parsed
        except Exception as e:
            print(f"Warning: could not read '{CREDENTIALS_FILE}': {e}")
    # Prompt
    creds = _prompt_credentials(existing=creds_from_file)
    # Save
    _save_credentials(CREDENTIALS_FILE, creds)
    print(f"Saved credentials to '{CREDENTIALS_FILE}'.")
    return creds


def _save_session(path: str, session_id: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(session_id.strip() + "\n")
        print(f"Saved session id to '{path}'.")
    except Exception as e:
        print(f"Warning: could not write session file '{path}': {e}")


def login_and_get_session(ip: str, username: str, password: str) -> str | None:
    """Perform the two-step Dahua login and return a session id or None on failure."""
    url = f"http://{ip}/RPC2_Login"
    headers = {"Content-Type": "application/json"}

    # Step 1: get challenge
    payload_step1 = {
        "method": "global.login",
        "params": {"userName": username, "password": "", "clientType": "Web3.0"},
        "id": 4
    }

    print("=== First request (challenge) ===")
    print("Request:", json.dumps(payload_step1, indent=4, ensure_ascii=False))

    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload_step1), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        resp1 = r.json()
    except requests.exceptions.RequestException as e:
        print(f"\n⚠ Network error during the first request: {e}")
        return None
    except json.JSONDecodeError:
        print("\n⚠ Unexpected response (not JSON) during the first request.")
        return None

    print("Response:", json.dumps(resp1, indent=4, ensure_ascii=False))

    # Validate challenge response
    if not resp1.get("result") or "params" not in resp1:
        print("Error: challenge not received or invalid response:", resp1)
        return None

    realm = resp1["params"].get("realm")
    random_key = resp1["params"].get("random")
    temp_session = resp1.get("session")

    if not all([realm, random_key, temp_session]):
        print("Error: missing required fields in challenge response.")
        return None

    print("Received realm:", realm)
    print("Received random:", random_key)

    # Step 2: compute hash and login
    password_final_hash = calculate_dahua_auth_hash(username, password, realm, random_key)

    payload_step2 = {
        "method": "global.login",
        "params": {
            "userName": username,
            "password": password_final_hash,
            "clientType": "Web3.0",
            "authorityType": "Default",
            "passwordType": "Default"
        },
        "id": 5,
        "session": temp_session
    }

    print("\n=== Second request (login with password) ===")
    print("Request:", json.dumps(payload_step2, indent=4, ensure_ascii=False))
    print("Raw payload:", json.dumps(payload_step2))

    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload_step2), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        resp2 = r.json()
    except requests.exceptions.RequestException as e:
        print(f"\n⚠ Network error during the second request: {e}")
        return None
    except json.JSONDecodeError:
        print("\n⚠ Unexpected response (not JSON) during the second request.")
        return None

    print("\n" + "=" * 65)
    print("Response:", json.dumps(resp2, indent=4, ensure_ascii=False))

    if resp2.get("result"):
        session_id = resp2.get("session") or resp2.get("params", {}).get("session")
        print("\n✅ Working session received:", session_id)
        _save_session(SESSION_FILE, session_id)
        return session_id
    else:
        print("\n❌ Login error:", resp2)
        return None


if __name__ == "__main__":
    print("== Dahua VTO Login ==")
    creds = _get_credentials_interactive()
    ip = creds.get("ip", "").strip()
    username = creds.get("username", "").strip()
    password = creds.get("password", "")

    if not ip or not username or not password:
        print("✖ Missing IP, username, or password. Aborting.")
        raise SystemExit(1)

    session = login_and_get_session(ip, username, password)
    if session is None:
        raise SystemExit(2)
    # You can now continue with authenticated calls using `session`.
