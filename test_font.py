import requests

urls = [
    "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
    "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf",
    "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
]

for url in urls:
    try:
        r = requests.head(url, allow_redirects=True)
        print(f"URL: {url} -> Status: {r.status_code}")
        if r.status_code == 200:
            content_type = r.headers.get('Content-Type')
            content_length = r.headers.get('Content-Length')
            print(f"  Content-Type: {content_type}, Length: {content_length}")
    except Exception as e:
        print(e)
