from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "Simple test endpoint working",
            "status": "success",
            "method": "GET"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Read request body
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
        except Exception as e:
            request_data = {"error": str(e)}
        
        response = {
            "message": "Simple POST test endpoint working",
            "status": "success",
            "method": "POST",
            "received_data": request_data
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return