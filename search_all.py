import os, glob

for filepath in glob.glob("components/*.py") + ["app.py"]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if "border-bottom" in line.lower() and "blue" not in line.lower() and "transparent" not in line.lower():
                print(f"{filepath}:{i+1}: {line.strip()}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
