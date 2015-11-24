## Dependencies
- python 3.x
- MongoDB
- pip
- Docker (optional)

## Running manually
```
$ pyvenv venv
$ . venv/bin/activate
$ pip install -r ./requirements.txt
$ mongod --config /usr/local/etc/mongod.conf&
$ ./run-services.sh
```

Then you can run tests:
```
$ py.test -v
```

## Running with Docker
```
$ docker-compose build
$ docker-compose up -d
$ docker exec -it taxi_rest_1 py.test
```
