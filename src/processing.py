import logging
import time
from models import drivers, orders

logger = logging.getLogger("processing")


def match():
    while True:
        order = orders.pick()
        if order:
            logger.info("picked order %s", order)
            driver = drivers.pick(order)
            if driver:
                logger.info("assigned driver %s", driver)
            else:
                logger.info("no available drivers, putting back to queue")
                orders.set(order["_id"], { "status": "new" })
                break
        else:
            break


def main_loop():
    while True:
        try:
            match()
            time.sleep(0.1)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main_loop()
