import os, glob

for filepath in glob.glob("components/*.py") + ["app.py", "add_format.py"]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if "00B0F0" in line.upper():
                print(f"{filepath}:{i+1}: {line.strip()}")
    except Exception as e:
        pass
