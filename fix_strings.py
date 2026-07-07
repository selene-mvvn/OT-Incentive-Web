
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace corrupted menu strings
replacements = [
    ('谿区･ｭ莉｣險育ｮ・', '残業代計算'),
    ('D盻ｮ LI盻・ D盻ｰ ﾃ¨', 'D? LI?U D? AN'),
    ('繝励Ο繧ｸ繧ｧ繧ｯ繝・', 'プロジェクト'),
    ('NH蘯ｬP Hﾃ?NG LO蘯T', 'NH?P HANG LO?T'),
    ('荳?諡ｬ蜈･蜉・', '一括入力'),
    ('繧､繝ｳ繧ｻ繝ｳ繝・ぅ繝・', 'インセンティブ'),
    ('L盻海H S盻ｬ THAO Tﾃ，', 'L?CH S? THAO TAC'),
    ('謫堺ｽ懷ｱ･豁ｴ', '操作履歴'),
    ('Cﾃ?I ﾄ雪ｺｶT CHUNG', 'CAI ??T CHUNG'),
    ('荳?闊ｬ險ｭ螳・', '一般設定'),
    ('Hﾆｰ盻嬾g d蘯ｫn s盻ｭ d盻･ng', 'H??ng d?n s? d?ng'),
    ('菴ｿ縺・婿繧ｬ繧､繝・', '使い方ガイド')
]

for bad, good in replacements:
    text = text.replace(bad, good)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

