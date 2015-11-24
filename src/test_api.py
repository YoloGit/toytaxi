import pytest
import requests
import time
from datetime import datetime, timedelta

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
            time.sleep(0.2) # I know, I know, sleep in tests...


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


@pytest.fixture
def clean_setup():
    # I prefer "clean setup" technique, when everything is deleted *before* test
    # This way, we have artifacts to play with in case of test failure
    requests.delete(DRIVER_API).raise_for_status()
    requests.delete(ORDER_API).raise_for_status()


def test_ride_now(clean_setup):
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


def test_wait_for_available_car(clean_setup):
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


def test_cancel_by_user(clean_setup):
    pass


def test_closest_driver(clean_setup):
    driver1 = TestDriver(location=[-71.058880, 42.360082])
    driver2 = TestDriver(location=[-74.005941, 40.712784])
    order = TestOrder(location=[-73.944158, 40.678178], status="new", uid=100)

    new_order_id = driver2.wait_for_order(location=[-74.005941, 40.712784])
    assert new_order_id == order.id

    order.update_status("accepted")
    order.update_status("completed")


def test_one_driver_n_users(clean_setup):
    location = [-73.944158, 41.678178]
    order1 = TestOrder(
        location=location,
        status="new",
        uid=100
    )
    order2 = TestOrder(
        location=location,
        status="new",
        uid=101,
        time=(datetime.now()).isoformat()
    )
    driver = TestDriver()

    # Pick and complete first order
    new_order_id = driver.wait_for_order(location)
    assert new_order_id == order1.id
    order1.update_status("completed")

    # Pick and complete second order
    new_order_id = driver.wait_for_order(location)
    assert new_order_id == order2.id
    order2.update_status("completed")


def test_ride_scheduled(clean_setup):
    # create driver
    driver = TestDriver(location=[-73.944158, 40.678178])

    # require a ride with pickup time in 1 sec
    user_loc = [-73.971249, 40.783060]
    pickup = datetime.now() + timedelta(0, 1)
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
    time.sleep(2)

    # Driver shoud be assigned by now
    upd = driver.track(user_loc)
    assert upd["order"] == order.id

    order.update_status("accepted")
    order.update_status("completed")
