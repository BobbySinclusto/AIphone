FROM python:3.10.8-alpine

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /aiphone
WORKDIR /aiphone

COPY static ./static
COPY templates ./templates
COPY app.py config.py db_setup.sql game_db.py util.py worker.py wsgi.py .

CMD [ "./app.py" ]
