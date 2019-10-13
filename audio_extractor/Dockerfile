FROM python:3.7
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["worker.py"]