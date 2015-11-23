FROM python

ADD src /taxi
ADD requirements.txt /taxi/
WORKDIR /taxi

RUN pip install -r ./requirements.txt

ENV MONGO_HOST mongo
