#!/usr/bin/env python3
"""
Local development server for previewing HTML newsletters.

This tool provides a simple local server for testing HTML newsletter content
before sending via Gmail. Supports live reload and preview features.
"""

import http.server
import socketserver
import os
import re
from datetime import datetime
from pathlib import Path
import threading
import time
import json

PORT = 8000
HOST = 'localhost'

class NewsletterHTMLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'

        # Add cache control headers for static files
        if self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')

        return super().do_GET()

    def log_message(self, format, *args):
        # Custom logging for requests
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {self.address_string()} - {format % args}")

    def send_head(self):
        # Custom head handling for HTML files
        if self.path.endswith('.html'):
            try:
                # Serve HTML with proper content type
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')

                # Add newsletter-specific headers
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('X-Frame-Options', 'DENY')

                self.end_headers()

                # Read and serve HTML file
                if self.path == '/index.html':
                    self._serve_index_page()
                else:
                    return super().send_head()

            except Exception as e:
                self.send_error(500, f"Error reading HTML file: {str(e)}")
        else:
            return super().send_head()

    def _serve_index_page(self):
        # Serve newsletter index page with navigation
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newsletter Preview - AI Newsletter System</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .preview-area {{
            padding: 30px;
        }}

        .preview-frame {{
            width: 100%;
            height: 800px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .controls {{
            background: #f8f9fa;
            padding: 20px;
            border-top: 1px solid #e9ecef;
        }}

        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}

        .btn:hover {{
            background: #5a67d8;
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }}

        .status {{
            padding: 10px 20px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }}

        .status.online {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}

        .status.offline {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}

        .loading {{
            text-align: center;
            padding: 50px;
            color: #666;
        }}

        .error {{
            background: #fff3cd;
            color: #856404;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            border: 1px solid #ffeaa7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Newsletter Preview</h1>
            <p>AI Newsletter System - Local Development Server</p>
            <p style="font-size: 0.9em; opacity: 0.9;">
                {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
            </p>
        </div>

        <div class="preview-area">
            <h2>Live Preview</h2>
            <div class="loading" id="loading">
                Loading newsletter...
            </div>
            <iframe id="newsletterFrame" class="preview-frame"
                   style="display: none;"
                   sandbox="allow-scripts allow-same-origin allow-forms allow-modals">
            </iframe>
            <div id="errorMessage" class="error" style="display: none;">
            </div>
        </div>

        <div class="controls">
            <h3>Controls</h3>
            <button class="btn" onclick="refreshPreview()">🔄 Refresh Preview</button>
            <button class="btn" onclick="toggleFullscreen()">📱 Toggle Fullscreen</button>
            <button class="btn" onclick="downloadHTML()">💾 Download HTML</button>
            <a href="http://localhost:8000/tmp" class="btn">📁 Browse Files</a>

            <div class="status online">
                ✅ Server Status: Online & Running
            </div>
        </div>
    </div>

    <script>
        let currentUrl = '/tmp/latest_newsletter.html';

        function refreshPreview() {{
            const frame = document.getElementById('newsletterFrame');
            const loading = document.getElementById('loading');
            const error = document.getElementById('errorMessage');

            loading.style.display = 'block';
            frame.style.display = 'none';
            error.style.display = 'none';

            // Find the latest newsletter HTML file
            fetch('/tmp/')
                .then(response => response.text())
                .then(html => {{
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const htmlFiles = Array.from(doc.querySelectorAll('a[href*="newsletter"], a[href*="html"]'))
                        .map(link => link.href)
                        .filter(href => href.endsWith('.html'));

                    if (htmlFiles.length > 0) {{
                        // Get the most recent one
                        const latest = htmlFiles.sort((a, b) => {{
                            const timeA = new Date(a.match(/_(\d+)_/)[1]);
                            const timeB = new Date(b.match(/_(\d+)_/)[1]);
                            return timeB - timeA;
                        }})[0];

                        currentUrl = latest;
                        loadPreview(currentUrl);
                    }} else {{
                        error.innerHTML = 'No newsletter HTML files found in /tmp/ directory.';
                        error.style.display = 'block';
                        loading.style.display = 'none';
                    }}
                }})
                .catch(err => {{
                    error.innerHTML = 'Error fetching newsletter files: ' + err.message;
                    error.style.display = 'block';
                    loading.style.display = 'none';
                }});
        }}

        function loadPreview(url) {{
            const frame = document.getElementById('newsletterFrame');
            const loading = document.getElementById('loading');
            const error = document.getElementById('errorMessage');

            loading.style.display = 'block';
            frame.style.display = 'none';
            error.style.display = 'none';

            frame.src = url;

            frame.onload = function() {{
                loading.style.display = 'none';
                frame.style.display = 'block';
            }};

            frame.onerror = function() {{
                loading.style.display = 'none';
                error.innerHTML = 'Error loading newsletter preview. Please check the server logs.';
                error.style.display = 'block';
            }};
        }}

        function toggleFullscreen() {{
            const frame = document.getElementById('newsletterFrame');
            frame.requestFullscreen().catch(err => {{
                console.log('Fullscreen request failed:', err);
            }});
        }}

        function downloadHTML() {{
            if (!currentUrl) {{
                alert('No newsletter to download');
                return;
            }}

            fetch(currentUrl)
                .then(response => response.text())
                .then(html => {{
                    const blob = new Blob([html], {{ type: 'text/html' }});
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'newsletter_' + new Date().toISOString().replace(/[:.]/g, '-') + '.html';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                }})
                .catch(err => {{
                    console.error('Download error:', err);
                }});
        }}

        // Auto-refresh preview every 30 seconds
        setInterval(refreshPreview, 30000);

        // Load preview on page load
        window.addEventListener('load', refreshPreview);
    </script>
</body>
</html>
        """

        self.wfile.write(html.encode('utf-8'))

    def _get_log_file(self):
        return os.path.join(os.path.dirname(__file__), 'newsletter_server.log')

def run_server():
    """Run the development server."""
    print(f"🚀 Starting Newsletter Development Server...")
    print(f"   Host: http://{HOST}:{PORT}")
    print(f"   Preview: http://{HOST}:{PORT}/")
    print(f"   Browse files: http://{HOST}:{PORT}/tmp/")
    print(f"   Press Ctrl+C to stop")
    print()

    # Create tmp directory if it doesn't exist
    os.makedirs('./tmp', exist_ok=True)

    # Create server
    with socketserver.TCPServer((HOST, PORT), NewsletterHTMLHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        finally:
            httpd.server_close()

def monitor_and_serve():
    """Monitor newsletter changes and serve them."""
    def check_for_changes():
        """Check for new newsletter files and serve them."""
        newsletter_dir = './tmp'
        if not os.path.exists(newsletter_dir):
            os.makedirs(newsletter_dir)
            return

        # Find the latest newsletter HTML file
        html_files = []
        for filename in os.listdir(newsletter_dir):
            if filename.endswith('.html') and 'newsletter' in filename:
                filepath = os.path.join(newsletter_dir, filename)
                html_files.append((filename, filepath, os.path.getmtime(filepath)))

        if html_files:
            # Sort by modification time (newest first)
            html_files.sort(key=lambda x: x[2], reverse=True)

            # Check if we should restart with new server
            latest_file = html_files[0][1]
            print(f"📄 Latest newsletter: {html_files[0][0]}")

            # Try to serve with current server
            try:
                # Test if server is still running
                import urllib.request
                urllib.request.urlopen(f'http://{HOST}:{PORT}/', timeout=2)
            except:
                # Server is not running, restart it
                print("🔄 Restarting server for latest newsletter...")
                run_server()

    # Run change check every 30 seconds
    while True:
        check_for_changes()
        time.sleep(30)

if __name__ == "__main__":
    import sys

    if '--monitor' in sys.argv:
        # Run in monitor mode
        print("🔍 Newsletter Monitor Mode")
        print("   Watching for new newsletter files and restarting server as needed")
        print()
        monitor_and_serve()
    else:
        # Run normal server
        run_server()