with open('components/ot_excel.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('format="%d"', 'format=",d"')

with open('components/ot_excel.py', 'w', encoding='utf-8') as f:
    f.write(text)
