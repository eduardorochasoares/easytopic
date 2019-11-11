FROM python:3.7
# Install dependencies
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["worker.py"]
