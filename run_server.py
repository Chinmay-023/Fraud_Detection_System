import os
from dotenv import load_dotenv
from app import app, init_database, load_models

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    init_database()
    load_models()
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)
