import os

def check_file(path):
    if not os.path.exists(path):
        print(f"File {path} does not exist!")
        return
    size = os.path.getsize(path)
    print(f"File: {path}, Size: {size}")
    with open(path, 'rb') as f:
        head = f.read(20)
        print(f"Header bytes: {head}")

check_file("assets/fonts/Roboto-Regular.ttf")
check_file("assets/fonts/Roboto-Bold.ttf")
