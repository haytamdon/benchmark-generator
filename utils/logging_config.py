import logging

def setup_logging():
    """Setup the logging.
    """
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)