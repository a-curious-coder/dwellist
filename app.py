import os
from app import create_app

app = create_app()


def run():
    # Get environment variable port or use 5000
    port = int(os.environ.get("PORT", 5000))
    # Get environment variable host or use 0.0.0.0
    host = os.environ.get("HOST", "0.0.0.0")

    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    run()
