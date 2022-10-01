FROM python:3

RUN mkdir -p /opt/src/warehouseman
WORKDIR /opt/src/warehouseman

COPY applicationWarehouseman.py ./applicationWarehouseman.py
COPY configurationWarehouseman.py ./configurationWarehouseman.py
COPY roleCheck.py ./roleCheck.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/warehouseman"

ENTRYPOINT ["python", "./applicationWarehouseman.py"]
