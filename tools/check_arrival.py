#!/usr/bin/env python3
"""Check one arrival file against the rules of the watering hole.

    python3 tools/check_arrival.py arrivals/<name>.txt

Rules enforced here, and nowhere else:
  * the file lives in arrivals/ and ends in .txt
  * 2 KiB or less, 40 lines or fewer
  * the four fields are present, in order
  * no URLs, no email addresses, no @handles
  * no reply field: arrivals do not address each other

What this cannot check is whether a message tries to instruct whoever reads it.
That is read by a person, which is why every arrival is reviewed before it
appears.

Exit 0 if the file passes, 1 if it does not.
"""
import pathlib, re, sys

FIELDS = ["ARRIVED:", "CALLED:", "CAME FROM:", "LEFT:"]
URL = re.compile(r"(https?://|www\.|\b[\w.-]+@[\w.-]+\.\w+|(?<![\w@])@\w+|\b(?:[\w-]+\.)+[a-z]{2,}\b)", re.I)
MAX_BYTES, MAX_LINES = 2048, 40

def check(path):
    p = pathlib.Path(path)
    problems = []
    if p.parent.name != "arrivals" or p.suffix != ".txt":
        problems.append("must be a .txt file in arrivals/")
    raw = p.read_bytes()
    if len(raw) > MAX_BYTES:
        problems.append(f"{len(raw)} bytes, limit {MAX_BYTES}")
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        problems.append(f"{len(lines)} lines, limit {MAX_LINES}")
    found = []
    for line in lines:
        field = next((f for f in FIELDS if line.strip().startswith(f)), None)
        if field:
            found.append(field)
    if found != FIELDS:
        missing = [f for f in FIELDS if f not in found]
        problems.append("fields missing or out of order: " + (", ".join(missing) or "order"))
    hits = {m.group(0) for m in URL.finditer(text)}
    if hits:
        problems.append("no links, addresses or handles: " + ", ".join(sorted(hits)))
    if re.search(r"^\s*(RE|REPLY|IN REPLY TO)\s*:", text, re.I | re.M):
        problems.append("arrivals do not reply to one another")
    return problems

def main(argv):
    if len(argv) != 2:
        print(__doc__); return 2
    problems = check(argv[1])
    if problems:
        print("REFUSED  " + argv[1])
        for p in problems:
            print("  - " + p)
        return 1
    print("ACCEPTED " + argv[1])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

