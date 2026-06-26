"""beerfetch — entry point.

Starts the HTTP server on localhost:7778 and opens the browser.
"""

import threading
import webbrowser
from lib.server import BeerFetchServer

PORT = 7778


def main():
    server = BeerFetchServer(("127.0.0.1", PORT))
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"beerfetch running at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        t.join()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
