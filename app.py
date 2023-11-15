import os
from app import create_app

app = create_app()
# Get environment variable port or use 5000
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
