import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace any [role="dialog"] that is NOT already preceded by [data-testid="stModal"]
# We use a regex to find [role="dialog"] and replace it with [data-testid="stDialog"]
# Wait, replacing [role="dialog"] with [data-testid="stDialog"] might create duplicate selectors if [data-testid="stDialog"] is already there.
# Let's just remove [role="dialog"] and its following comma/space if it's paired with [data-testid="stDialog"]

# Actually, the easiest way is to replace `[role="dialog"] ` with `[data-testid="stDialog"] ` 
# and then just let duplicates exist (CSS allows duplicate selectors like `a, a { ... }`)
# Let's use re.sub to replace `[role="dialog"]` when it is not preceded by `stModal`

# But let's just do a simple string replace for the specific blocks.
# Wait! Instead of complex regex, let's just replace all `[role="dialog"]` with `div[data-testid="stModal"] [role="dialog"]`.
# But `div[data-testid="stModal"] [role="dialog"]` might become `div[data-testid="stModal"] div[data-testid="stModal"] [role="dialog"]`.

new_content = re.sub(r'(?<!div\[data-testid="stModal"\] )\[role="dialog"\]', r'div[data-testid="stModal"] [role="dialog"]', content)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Done replacing.")
