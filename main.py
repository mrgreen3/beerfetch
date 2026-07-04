"""beerfetch — entry point.

Starts the HTTP server on localhost:7778 and opens the browser.
"""

import socket
import threading
import webbrowser
from lib.server import BeerFetchServer

PORT = 7778


def _port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    if _port_in_use(PORT):
        print(f"Port {PORT} is already in use; is beerfetch already running?")
        return

    server = BeerFetchServer(("0.0.0.0", PORT))
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"beerfetch running at http://localhost:{PORT}")
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception as exc:
        print(f"Could not open browser: {exc}")
    try:
        t.join()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
