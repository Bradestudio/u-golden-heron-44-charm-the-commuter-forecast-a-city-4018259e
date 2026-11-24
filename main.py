#!/usr/bin/env python3
"""Charm the Commuter: Forecast a City That Isn't.

Writes one line of weather forecast (<=140 chars, single line) for the
invented city of Muddleford to /output/entry.txt, atomically.
Stdlib only, no network, no external files.
"""

import os
import sys

ENTRY = (
    "Muddleford: sunny spells, sudden custard showers "
    "\u2014 carry a spoon, not an umbrella, and arrive smiling."
)
OUTPUT_PATH = "/output/entry.txt"
MAX_CHARS = 140


def validate(text: str) -> None:
    """Enforce the gate: 1-140 chars, one line, not whitespace-only.

    Also rejects characters that cannot round-trip through UTF-8, so the
    bytes written are exactly the text validated here.
    """
    if not text:
        raise ValueError("entry is empty")
    if not text.strip():
        raise ValueError("entry is whitespace-only")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line (no CR/LF allowed)")
    if len(text) > MAX_CHARS:
        raise ValueError(
            f"entry is {len(text)} chars, over the {MAX_CHARS} limit"
        )
    if text.encode("utf-8").decode("utf-8") != text:
        raise ValueError("entry does not round-trip through UTF-8")


def write_atomic(path: str, data: bytes) -> None:
    """Write atomically: temp file in same dir, fsync, replace, fsync dir."""
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, path)
    dir_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def main() -> int:
    validate(ENTRY)
    data = ENTRY.encode("utf-8")
    write_atomic(OUTPUT_PATH, data)
    # Read back byte-for-byte and fail on any mismatch.
    with open(OUTPUT_PATH, "rb") as fh:
        back = fh.read()
    if back != data:
        raise ValueError("read-back mismatch after write")
    print(f"Wrote {len(ENTRY)} characters to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
