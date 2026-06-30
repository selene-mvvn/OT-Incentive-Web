import os
import codecs

directory = r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web'
for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.py'):
            filepath = os.path.join(root, filename)
            with codecs.open(filepath, 'r', 'utf-8') as f:
                content = f.read()
            if '\u2705' in content or '\U0001F6A8' in content:
                content = content.replace('icon="\u2705"', 'icon=":material/check_circle:"')
                content = content.replace('icon="\U0001F6A8"', 'icon=":material/error:"')
                content = content.replace('Đã xóa các mục đã chọn \u2705', 'Đã xóa các mục đã chọn')
                content = content.replace('Đã xóa toàn bộ lịch sử \u2705', 'Đã xóa toàn bộ lịch sử')
                content = content.replace('選択した項目を削除しました \u2705', '選択した項目を削除しました')
                content = content.replace('すべての履歴を削除しました \u2705', 'すべての履歴を削除しました')
                
                if 'ui_utils.py' in filename:
                    if 'icon=":material/check_circle:"' in content:
                         content = content.replace('icon=":material/check_circle:"', 'icon=":material/delete:"')

                with codecs.open(filepath, 'w', 'utf-8') as f:
                    f.write(content)
                print(f'Updated {filename}')
