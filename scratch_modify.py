import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
file_path = r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\action_history_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i < 18:
        new_lines.append(line)
    elif i == 18:
        new_lines.append('    with st.container():\n')
        new_lines.append('        from components.ui_utils import make_container_white\n')
        new_lines.append('        make_container_white()\n')
        new_lines.append('        # st.markdown("---")\n')
    else:
        if line.strip() == '':
            new_lines.append('\n')
        elif line.startswith('def '):
            new_lines.append(line)
        elif not line.startswith(' '):
            new_lines.append(line)
        else:
            new_lines.append('    ' + line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Success')
