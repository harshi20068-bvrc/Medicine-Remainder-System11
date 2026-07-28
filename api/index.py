"""
Vercel Serverless Function Handler for Medicine Reminder System API.
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {
            "status": "success",
            "message": "Medicine Reminder System API is active on Vercel Serverless environment.",
            "version": "1.1.0"
        }
        
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {
            "status": "success",
            "message": "Data received successfully."
        }
        
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
