FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY applicationWarehouseman.py ./applicationWarehouseman.py
COPY configurationWarehouseman.py ./configurationWarehouseman.py
COPY roleCheck.py ./roleCheck.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./applicationWarehouseman.py"]
