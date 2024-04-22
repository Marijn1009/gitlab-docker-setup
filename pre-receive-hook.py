#!/usr/bin/env python3
import sys
import re
import os

def check_filenames():
    for line in sys.stdin:
        old_rev, new_rev, ref_name = line.strip().split()
        cmd = f"git diff --name-only {old_rev} {new_rev}"
        with os.popen(cmd) as stream:
            for filename in stream:
                filename = filename.strip()
                if re.search(r'\s', filename):
                    print(f"Error: File '{filename}' contains whitespace.")
                    return 1
    return 0

if __name__ == "__main__":
    sys.exit(check_filenames())
