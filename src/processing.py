import logging
import datetime
import time
from models import drivers, orders

logger = logging.getLogger("taxi-processing")


def pick_order():
    return orders.find_and_set(
        {
            "status": "new",
            "$or": [
                { "pickup_time": { "$lte": datetime.datetime.now() } },
                { "pickup_time": None }
            ]
        },
        { "status": "processing" },
        sort=[("pickup_time", 1)]
    )


def pick_driver(order):
    return drivers.find_and_set(
        { "order": None, "location": {"$near": order["location"]} },
        { "order": order["_id"] }
    )


def match():
    while True:
        order = pick_order()
        if order:
            logger.info("picked order %s", order)
            driver = pick_driver(order)
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
