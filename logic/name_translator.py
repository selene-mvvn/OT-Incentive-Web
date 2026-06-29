import unicodedata

# Dictionary mapping common Vietnamese syllables (without tone marks) to Katakana.
VN_TO_KANA = {
    'nguyen': 'グエン', 'tran': 'チャン', 'le': 'レー', 'pham': 'ファム',
    'hoang': 'ホアン', 'huynh': 'フイン', 'phan': 'ファン', 'vu': 'ヴー',
    'vo': 'ヴォー', 'dang': 'ダン', 'bui': 'ブイ', 'do': 'ドー',
    'ho': 'ホー', 'ngo': 'ゴー', 'duong': 'ズオン', 'ly': 'リー',
    'anh': 'アン', 'tu': 'トゥー', 'tuan': 'トゥアン', 'son': 'ソン',
    'minh': 'ミン', 'duc': 'ドゥック', 'hung': 'フン', 'huy': 'フイ',
    'hai': 'ハイ', 'ha': 'ハー', 'huong': 'フオン', 'hoa': 'ホア',
    'lan': 'ラン', 'ngoc': 'ゴック', 'trang': 'チャン', 'thao': 'タオ',
    'phuong': 'フオン', 'linh': 'リン', 'van': 'ヴァン', 'thi': 'ティ',
    'dat': 'ダット', 'kien': 'キエン', 'trung': 'チュン', 'quang': 'クアン',
    'thanh': 'タイン', 'binh': 'ビン', 'cuong': 'クオン',
    'hieu': 'ヒエウ', 'kha': 'カー', 'khoa': 'コア', 'nam': 'ナム',
    'phat': 'ファット', 'tai': 'タイ', 'tien': 'ティエン', 'toan': 'トアン',
    'truong': 'チュオン', 'bao': 'バオ', 'chi': 'チー', 'chau': 'チャウ',
    'diep': 'ジエップ', 'dung': 'ズン', 'giang': 'ザン', 'han': 'ハン',
    'kieu': 'キエウ', 'mai': 'マイ', 'nhi': 'ニー', 'nhu': 'ニュー',
    'oanh': 'オアン', 'quynh': 'クイン', 'tam': 'タム', 'thuy': 'トゥイ',
    'tram': 'チャム', 'uyen': 'ウエン', 'vy': 'ヴィー',
    'yen': 'イエン', 'phuc': 'フック', 'sang': 'サン', 'thang': 'タン',
    'thien': 'ティエン', 'thinh': 'ティン', 'tri': 'チー', 'trieu': 'チエウ',
    'trong': 'チョン', 'dong': 'ドン', 'kham': 'カム', 'luong': 'ルオン',
    'nghi': 'ギー', 'nghia': 'ギア', 'phong': 'フォン', 'quan': 'クアン',
    'quoc': 'クオック', 'sinh': 'シン', 'thai': 'タイ', 'tho': 'トー',
    'thuong': 'トゥオン', 'tuyen': 'トゥエン', 'dai': 'ダイ', 'hao': 'ハオ',
    'hinh': 'ヒン', 'ky': 'キー', 'manh': 'マイン', 'ngon': 'ゴン',
    'nhat': 'ニャット', 'phap': 'ファップ', 'phi': 'フィー', 'quy': 'クイ',
    'tao': 'タオ', 'thach': 'タック', 'tiep': 'ティエップ', 'tinh': 'ティン',
    'to': 'トー', 'tuong': 'トゥオン', 'vinh': 'ヴィン', 'vuong': 'ヴオン',
    'nhan': 'ニャン', 'loc': 'ロック', 'long': 'ロン', 'phu': 'フー',
    'kim': 'キム', 'son': 'ソン', 'thuan': 'トゥアン', 'phuc': 'フック'
}

def remove_accents(input_str):
    s1 = unicodedata.normalize('NFKD', input_str).encode('ASCII', 'ignore').decode('utf-8')
    s1 = s1.replace('đ', 'd').replace('Đ', 'D')
    return s1

def translate_vn_name_to_kana(full_name):
    if not full_name:
        return ''
    
    clean_name = remove_accents(full_name).lower()
    words = clean_name.split()
    kana_words = []
    
    for word in words:
        if word in VN_TO_KANA:
            kana_words.append(VN_TO_KANA[word])
        else:
            kana_words.append(word.upper())
            
    return '・'.join(kana_words)
