FROM python:3.11.1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update && apt-get install -y wait-for-it
RUN --mount=type=bind,target=/app/,source=.,rw \
pip install -r /app/requirements.txt
CMD ./run.sh