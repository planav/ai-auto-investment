#!/usr/bin/env python3
"""
Secret key generator for AutoInvest.

Generates a cryptographically-secure random SECRET_KEY and either prints it
to the console or writes it directly into backend/.env.

Usage
-----
Print a new key (copy & paste into .env manually):

    python scripts/generate_secret_key.py

Auto-write the key into backend/.env (creates the file from .env.example if
it does not exist yet):

    python scripts/generate_secret_key.py --write
"""

import argparse
import os
import re
import secrets


ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
ENV_EXAMPLE_FILE = os.path.join(os.path.dirname(ENV_FILE), ".env.example")


def generate_key() -> str:
    """Return a 64-character cryptographically-secure hex string (256-bit entropy)."""
    return secrets.token_hex(32)


def write_key_to_env(key: str) -> None:
    """
    Write *key* as the SECRET_KEY value in backend/.env.

    - If the file does not exist it is created from .env.example.
    - If SECRET_KEY is already present its value is replaced.
    - If SECRET_KEY is absent the line is appended.
    """
    # Bootstrap from example file when .env is missing
    if not os.path.exists(ENV_FILE):
        if os.path.exists(ENV_EXAMPLE_FILE):
            with open(ENV_EXAMPLE_FILE) as src:
                content = src.read()
            print(f"Created {ENV_FILE} from .env.example")
        else:
            content = ""
            print(f"Created new {ENV_FILE}")
    else:
        with open(ENV_FILE) as fh:
            content = fh.read()

    new_line = f"SECRET_KEY={key}"
    pattern = re.compile(r"^SECRET_KEY=.*$", re.MULTILINE)

    if pattern.search(content):
        content = pattern.sub(new_line, content)
    else:
        # Ensure the file ends with a newline before appending
        if content and not content.endswith("\n"):
            content += "\n"
        content += new_line + "\n"

    with open(ENV_FILE, "w") as fh:
        fh.write(content)

    print(f"SECRET_KEY written to {ENV_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a random SECRET_KEY for the AutoInvest backend."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the generated key directly into backend/.env (replaces any existing SECRET_KEY).",
    )
    args = parser.parse_args()

    key = generate_key()

    print("\nAutoInvest — Secret Key Generator")
    print("=" * 40)
    print(f"\nGenerated SECRET_KEY:\n\n  {key}\n")

    if args.write:
        write_key_to_env(key)
        print("\nYou can now start the application.")
    else:
        print("Copy the key above and set it in backend/.env:")
        print("  SECRET_KEY=<the key above>")
        print("\nOr re-run with --write to do this automatically:")
        print("  python scripts/generate_secret_key.py --write\n")


if __name__ == "__main__":
    main()
