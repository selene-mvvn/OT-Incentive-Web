import http.server
class handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        with open('dom_dump.html', 'wb') as f:
            f.write(post_body)
        self.send_response(200)
        self.end_headers()
http.server.HTTPServer(('', 8080), handler).serve_forever()
