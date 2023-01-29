FROM python:3.10.2

WORKDIR /backend

COPY ./requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5001

COPY . .

CMD [ "python", "engine.py" ]