import os
import http.server
import socketserver

ip = 'localhost' 
port = '8000' 
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer((ip, int(port)), Handler)
httpd.serve_forever()
