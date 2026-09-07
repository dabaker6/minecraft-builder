import logging
import sys

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        stream=sys.stderr,        # everything to stderr
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

