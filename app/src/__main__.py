#!/usr/bin/env python3

# If __main__.py is present in a Python module, it will be executed by default
# if that module is executed, e.g., `python -m my.module`.
#
# https://docs.python.org/3/library/__main__.html

import logging
import uvicorn
import src.app
#import src.logging
from src.app_config import AppConfig
from src.util.local import load_local_env_vars

#logger = logging.getLogger(__package__)

def main() -> None:
    load_local_env_vars()
    app_config = AppConfig()

    environment = app_config.environment

    # When running in a container, the host needs to be set to 0.0.0.0 so that the app can be
    # accessed from outside the container. See Dockerfile
    host = app_config.host
    port = app_config.port

    #logger.info(
    #    "Running API Application", extra={"environment": environment, "host": host, "port": port}
    #)
#    setattr("__main__", "app", app)

    if app_config.environment == "local":
        # If python files are changed, the app will auto-reload
        # Note this doesn't have the OpenAPI yaml file configured at the moment
        uvicorn.run("app:create_app", host=host, port=port, reload=True)
    else:
        # Don't enable the reloader if non-local
        uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
