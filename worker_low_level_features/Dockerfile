FROM python:3.7
COPY . /app
WORKDIR /app



RUN export CFLAGS="-I /usr/local/lib/python3.7/site-packages/numpy/core/include/numpy $CFLAGS"

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]

CMD ["worker.py"]