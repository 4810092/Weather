#!/usr/bin/env python3
"""Run a command with a portable TERM-then-KILL timeout."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("timeout_seconds", type=float)
    parser.add_argument("grace_seconds", type=float)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.timeout_seconds <= 0 or args.grace_seconds < 0:
        parser.error("timeouts must be positive and grace must not be negative")
    if args.command[:1] == ["--"]:
        args.command = args.command[1:]
    if not args.command:
        parser.error("a command is required after --")
    return args


def terminate_group(process: subprocess.Popen[bytes], sig: signal.Signals) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, sig)
    except ProcessLookupError:
        pass


def main() -> int:
    args = parse_args()
    process = subprocess.Popen(args.command, start_new_session=True)
    try:
        return process.wait(timeout=args.timeout_seconds)
    except subprocess.TimeoutExpired:
        terminate_group(process, signal.SIGTERM)
        try:
            process.wait(timeout=args.grace_seconds)
        except subprocess.TimeoutExpired:
            terminate_group(process, signal.SIGKILL)
            process.wait()
        return 124
    except KeyboardInterrupt:
        terminate_group(process, signal.SIGINT)
        try:
            return process.wait(timeout=args.grace_seconds)
        except subprocess.TimeoutExpired:
            terminate_group(process, signal.SIGKILL)
            process.wait()
            return 130


if __name__ == "__main__":
    sys.exit(main())
