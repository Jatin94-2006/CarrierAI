import logging
import sys

def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Mask secrets in log messages
    return logging.getLogger("ctbf_module_1")

logger = setup_logging()
