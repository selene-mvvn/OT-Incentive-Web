import re

with open('components/incentive_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add st.rerun() after `st.success(t("Đã thêm vào danh sách!", "リストに追加しました！"))`
text = text.replace(
    'st.success(t("Đã thêm vào danh sách!", "リストに追加しました！"))',
    'st.success(t("Đã thêm vào danh sách!", "リストに追加しました！"))\n                st.rerun()'
)

# 2. Extract the Ranking section (lines 288-377)
# It starts at:
#     # ==========================
#     # TAB 2: RANKING & CHARTS
#     # ==========================
#     if 'last_incentive_calc' in st.session_state:
#         st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('BẢNG XẾP HẠNG HIỆU SUẤT'
# and goes to the end of the file.

pattern_ranking = r"    # ==========================\n    # TAB 2: RANKING & CHARTS.*"
match_ranking = re.search(pattern_ranking, text, flags=re.DOTALL)
ranking_code = match_ranking.group(0)

# 3. Remove the Ranking section from the end
text = text.replace(ranking_code, "")

# 4. Remove the Charts section
# Starts at: `        # Charts`
# Ends right before `        # Add to List button`
pattern_charts = r"        # Charts.*?        # Add to List button"
# Wait, let's just replace it with `        # Add to List button` and prepend the Ranking code there!
# But wait, the Ranking code is inside `if 'last_incentive_calc' in st.session_state:`, which is ALREADY the current scope of the Charts block!
# Let's clean up `ranking_code`. We don't need the `if 'last_incentive_calc' in st.session_state:` check since we will inject it inside an existing one.
ranking_inner_code = ranking_code.replace("    if 'last_incentive_calc' in st.session_state:\n", "")
# It is indented by 8 spaces now. We need to keep it at 8 spaces.
# Wait, `ranking_code` has `st.markdown(...)` indented at 8 spaces because of the `if`. 
# We can just inject it directly.

replacement = ranking_inner_code + "\n\n        # Add to List button"
text = re.sub(pattern_charts, replacement, text, flags=re.DOTALL)

with open('components/incentive_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Success")
