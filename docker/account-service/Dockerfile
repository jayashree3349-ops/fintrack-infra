FROM python:3.12-alpine

WORKDIR /app

COPY app/server.py .

ENV APP_NAME=account-service
ENV APP_VERSION=v1
ENV PORT=8080

EXPOSE 8080

CMD ["python", "server.py"]
