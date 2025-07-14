import http.server
import socketserver
import os
import threading

PORT = 8000

if __name__ == "__main__":
    # Serve files from this script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"📡 Serving HTTP on port {PORT}.")
        print(f"🔗  http://localhost:{PORT}/dashboard.html")

        # Start a thread to listen for Enter key to shut down
        def wait_for_enter():
            input("\nPress Enter to stop the server...\n")
            httpd.shutdown()

        threading.Thread(target=wait_for_enter, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

        print("🛑 Server stopped.")
