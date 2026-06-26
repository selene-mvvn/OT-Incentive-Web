import re

def add_format(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # We want to insert `format="%,d"` after NumberColumn(
    # But only if it doesn't already have format
    text = re.sub(r'st\.column_config\.NumberColumn\((?!.*format=)(.*?)\)', 
                  r'st.column_config.NumberColumn(\1, format="%,d")', 
                  text)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

add_format('components/ot_manual.py')
add_format('components/ot_excel.py')
