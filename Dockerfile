FROM python:3.9-slim-buster
WORKDIR /app
COPY . .
RUN apt update && apt install -y gcc
RUN pip install -r requirements.txt
CMD ["python", "run.py"]