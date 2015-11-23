import requests
import datetime
import time

HOST = "localhost"
ORDER_API = "http://%s:5000/orders" % HOST
DRIVER_API = "http://%s:5000/drivers" % HOST


class TestDriver:
    def __init__(self, **params):
        r = requests.post(DRIVER_API, json=params)
        r.raise_for_status()
        self.id = r.json()["id"]
        self.url = "%s/%s" % (DRIVER_API, self.id)


    def track(self, location):
        r = requests.patch(self.url, json={
            "location": location
        })
        r.raise_for_status()
        return r.json()

    def wait_for_order(self, location):
        while True:
            upd = self.track(location)
            if "order" in upd:
                return upd["order"]
            time.sleep(0.2)


class TestOrder:
    def __init__(self, **params):
        r = requests.post(ORDER_API, json=params)
        r.raise_for_status()
        self.id = r.json()["id"]
        self.url = "%s/%s" % (ORDER_API, self.id)

    def update_status(self, status):
        r = requests.patch(self.url, json={
            "status": status
        })
        r.raise_for_status()
        assert r.json()["status"] == status

    def get_status(self):
        r = requests.get(self.url)
        r.raise_for_status()
        return r.json()["status"]


def test_ride_now():
    # create a driver
    driver = TestDriver(location=[-73.944158, 40.678178])

    # require a ride
    user_loc = [-73.971249, 40.783060]
    order = TestOrder(
        location=user_loc,
        uid=100,
        status="new"
    )

    # driver updates position and gets notified about new order
    new_order_id = driver.wait_for_order([-73.944158, 40.678178])
    assert new_order_id == order.id

    # driver acceptes the order and going to pick up the passenger
    order.update_status("accepted")
    # driver picked up the passenger and heading to the location
    order.update_status("in_progress")
    # driver updates order status to done
    order.update_status("completed")

    # TODO: free car, celanup other stuff


def test_ride_wait():
    # require a ride
    user_loc = [-73.971249, 40.783060]
    order = TestOrder(
        location=user_loc,
        uid=100,
        status="new"
    )

    # make sure that the order is new
    assert order.get_status() == "new"

    # create a driver
    driver = TestDriver(location=user_loc)

    # do pick up
    new_order_id = driver.wait_for_order(user_loc)
    assert new_order_id == order.id

    order.update_status("accepted")
    order.update_status("completed")


def test_ride_cancel():
    pass


def test_closest_driver():
    pass


def test_ride_scheduled():
    # create driver
    driver = TestDriver(location=[-73.944158, 40.678178])

    # require a ride with pickup in 1 sec
    user_loc = [-73.971249, 40.783060]
    pickup = datetime.datetime.now()+datetime.timedelta(0, 1)
    order = TestOrder(
        location=user_loc,
        uid=100,
        status="new",
        pickup_time=pickup.isoformat()
    )

    assert order.get_status() == "new"

    # Make sure the order is not assigned yet
    upd = driver.track(user_loc)
    assert "order" not in upd

    # Kill me for using sleep in tests,
    # but c'cmon, mocks are hard!
    time.sleep(1.5)

    # Driver shoud be assigned by now
    upd = driver.track(user_loc)
    assert upd["order"] == order.id

    order.update_status("accepted")
    order.update_status("completed")
