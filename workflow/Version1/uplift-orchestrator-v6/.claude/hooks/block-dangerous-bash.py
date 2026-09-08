#!/usr/bin/env python3
"""V5 conceptual PreToolUse guard for destructive Git operations.

The Claude Code integration should adapt this hook to the exact hook payload/environment
available in the installed Claude Code version. The authoritative safety model remains
permissions + hook + post-execution inspection.
"""
import re
import sys

blocked = [
    r"git\s+reset\s+--hard",
    r"git\s+clean\s+-[^\n]*f",
    r"git\s+push\s+[^\n]*--force(?:-with-lease)?",
    r"git\s+push\s+[^\n]*\s-f(?:\s|$)",
    r"git\s+rebase\s+-i",
    r"git\s+filter-repo",
    r"git\s+branch\s+-D",
]

command = " ".join(sys.argv[1:])
for pattern in blocked:
    if re.search(pattern, command, re.IGNORECASE):
        print(f"BLOCKED: destructive Git operation matches policy: {pattern}", file=sys.stderr)
        raise SystemExit(2)
raise SystemExit(0)
