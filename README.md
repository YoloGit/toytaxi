## Setting up and running
### Dependencies
- python 3.x
- MongoDB
- pip
- Docker (optional)

### Running manually
```
$ pyvenv venv
$ . venv/bin/activate
$ pip install -r ./requirements.txt
$ mongod --config /usr/local/etc/mongod.conf&
$ cd src && ./run-services.py
```

Then you can run tests:
```
$ py.test -v
```

### Running with Docker
```
$ docker-compose build
$ docker-compose up -d
$ docker exec -it taxi_rest_1 py.test
```

## Architecture
The system is split in two services: API server (rest.py) and processing server (processing.py). API server just provides a REST API for drivers and clients, while processing server periodically checks the database for new orders and matches them with available drivers.

Both services are stateless and therefore can be run in multiple instances. The system relies on MongoDB ability to atomically [find and modify](https://docs.mongodb.org/manual/reference/command/findAndModify/) documents.

The orders are sorted by pickup time and processed in this order. I was considering using a *real* queue like RabbitMQ but decided to keep it simple and stick to MongoDB. Besides, MongoDB [seems to be good](https://www.mongodb.com/presentations/mongodb-message-queue) at this task. The only downside of this approach is the lack of any push mechanism, so we have to periodically query the database. But since we are not trying to save battery life, it's a decent aproach.

I decided to use REST not because it's a de facto standard, but because its "representation of state" ideology perfectly suites mobile clients who can lose connection or simply crash. But in real world we would obviously use a combination of pull and server side push notifications.

Authorization is not implemented for the sake of simplicity.

# API
The API has only two resources: /drivers and /orders. Users POST their driver requests to /orders and the periodically check the them. Drivers register themselves by posting to /drivers and the update their location using a PATCH method to /drivers/:driverid. PATCH always return the whole document and if "order" field is set, then the driver has a job to do. When driver recieves new order id, he simply updates the order status by patching /orders/:orderid. 

See [tests](https://github.com/szastupov/toytaxi/blob/master/src/test_api.py) for more examples.
