FROM python:3.12-alpine

WORKDIR /app

ARG APP_VERSION=v1

COPY app/server.py .

ENV APP_NAME=account-service
ENV APP_VERSION=${APP_VERSION}
ENV PORT=8080

EXPOSE 8080

CMD ["python", "server.py"]
