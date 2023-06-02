import logging
import os

from fastapi import FastAPI
#import src.adapters.db as db
#import src.adapters.db.flask_db as flask_db
import src.logging
from src.logging.flask_logger import FastAPILoggerMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI() #? __name__
    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    # Add logging middleware
    app.add_middleware(FastAPILoggerMiddleware, logger=logger)

    # TODO: db connection
    # db_client = db.PostgresDBClient()
    # flask_db.register_db_client(db_client, app)

    # TODO: configuration
    # configure_app(app)
    # TODO: routes
    # register_blueprints(app)

    return app