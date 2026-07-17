import sys
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "00B0F0" in line.upper():
        print(f"{i+1}: {line.strip()}")
