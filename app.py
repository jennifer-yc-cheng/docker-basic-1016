#!/usr/bin/env python3
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8000
REDIS_HOST = os.environ.get("REDIS_HOST", "")

PAGE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="utf-8"><title>哈囉，Docker！</title></head>
<body>
<h1>哈囉，Docker！</h1>
<p>容器主機名稱：{hostname}</p>
<p>你是第 {count} 位訪客</p>
<p>Redis 狀態：{redis_status}</p>
</body>
</html>
"""


def get_visit_count():
    """回傳 (次數, 狀態文字)。"""
    if not REDIS_HOST:
        return "—", "未設定（單機模式）"
    try:
        import redis
        client = redis.Redis(host=REDIS_HOST, port=6379, socket_connect_timeout=2)
        n = client.incr("visits")
        return n, "已連線"
    except Exception as exc:  
        return "—", "連線失敗：{}: {}".format(type(exc).__name__, exc)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        count, status = get_visit_count()
        body = PAGE.format(
            hostname=socket.gethostname(),
            count=count,
            redis_status=status,
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    httpd = HTTPServer(("0.0.0.0", PORT), Handler)
    print("Serving on 0.0.0.0:{}".format(PORT), flush=True)
    httpd.serve_forever()
