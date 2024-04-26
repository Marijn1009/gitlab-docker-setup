#!/usr/bin/env python3
import sys
import re
import subprocess

def check_filenames():
    # Read from stdin
    for line in sys.stdin:
        old_rev, new_rev, ref_name = line.strip().split()

        # Use subprocess to call git diff and get the list of changed filenames
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', old_rev, new_rev],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            # Handle possible git command errors (e.g., bad revisions)
            print(f"Error running git diff: {e}", file=sys.stderr)
            return 1

        filenames = result.stdout.splitlines()

        for filename in filenames:
            if filename.endswith('.sql'):
                if re.search(r'\s', filename):
                    print(f"Error: .Filename '{filename}' contains whitespace.", file=sys.stderr)
                    return 1

    # Everything valid:
    return 0

if __name__ == "__main__":
    sys.exit(check_filenames())
