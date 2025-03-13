FROM python:3.10.12-bullseye
RUN mkdir -p /var/www/mindkraft 
COPY . /var/www/mindkraft/
WORKDIR /var/www/mindkraft/
RUN apt-get update -y
RUN apt-get install python3-dev libldap2-dev libsasl2-dev -y
RUN apt-get install redis
RUN pip install -r requirements.txt
CMD ["python3","manage.py","runsslserver"]
