# syntax=docker/dockerfile:1
FROM python:3.9.19-slim-bullseye
RUN pip install flask obs-websocket-py python-dotenv
COPY app .
CMD ["python", "-u", "app.py"]