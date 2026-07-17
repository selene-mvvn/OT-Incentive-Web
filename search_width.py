import sys
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "width" in line.lower():
        print(f"{i+1}: {line.strip()}")
