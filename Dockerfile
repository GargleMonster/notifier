FROM python:3.12.0b4-alpine3.18

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "waitress-serve --host 127.0.0.1 --call 
