FROM python:3

RUN mkdir -p /opt/src/buyer
WORKDIR /opt/src/buyer

COPY applicationBuyer.py ./applicationBuyer.py
COPY configuration.py ./configuration.py
COPY roleCheck.py ./roleCheck.py
COPY models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/buyer"

ENTRYPOINT ["python", "./applicationBuyer.py"]
