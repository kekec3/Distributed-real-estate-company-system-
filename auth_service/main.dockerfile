FROM python:3

ENV PYTHONUNBUFFERED=1

RUN mkdir /auth_service

WORKDIR /auth_service

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENTRYPOINT [ "python", "main.py" ]