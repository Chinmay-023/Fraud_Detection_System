import os
from app import app, init_database, load_models


if __name__ == "__main__":
    init_database()
    load_models()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)
