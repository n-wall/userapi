
from api.app import app

#app=api.app.app


import os
import uvicorn
if __name__ == "__main__":
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", default=5000)),
        log_level="info"
    )
    server = uvicorn.Server(config)
    server.run()
