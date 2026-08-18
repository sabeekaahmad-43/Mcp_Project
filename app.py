from flask import Flask
from routes.mcp_routes import mcp_bp
from routes.chat_routes import chat_bp
from agent import register_local_tools
import config

app = Flask(__name__)

register_local_tools()

app.register_blueprint(mcp_bp, url_prefix="/api/mcp")
app.register_blueprint(chat_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(port=config.FLASK_PORT, debug=True)