import logging
import sys
import os
from datetime import datetime

class setup_logger():
    log_dir = './logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, f"app_run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

    log_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(
        filename=log_file_path,
        mode='a'
    )
    file_handler.setFormatter(log_formatter)

    stream_handler = logging.StreamHandler(
        stream=sys.stdout
    )
    stream_handler.setFormatter(log_formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, stream_handler],
        force=True
    )

