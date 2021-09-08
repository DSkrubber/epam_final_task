FROM python:3.9.7-slim
WORKDIR /final_task
COPY . .
RUN pip install --no-cache-dir -r requirements.txt