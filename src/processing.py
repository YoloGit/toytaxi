import logging
import time
from models import drivers, orders

logger = logging.getLogger("processing")

def match_order(order):
    logger.info("matching order %s...", order)
    driver = drivers.pick(order)
    if driver:
        logger.info("assigned driver %s", driver)
    else:
        logger.info("no available drivers, putting back to queue")
        orders.set(order["_id"], { "status": "new" })


def match():
    """Pick ready to go orders and assign drivers if available"""
    while True:
        order = orders.pick()
        if order:
            match_order(order)
        else:
            time.sleep(0.1) # Should be tuned for production use


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        match()
    except KeyboardInterrupt:
        logging.info("processing interrupted by user")
