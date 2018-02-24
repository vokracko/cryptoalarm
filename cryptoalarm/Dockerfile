FROM python:3
ADD Coin.py /
ADD Database.py /
ADD Notifier.py /
ADD cryptoalarm.py /
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD [ "python", "./cryptoalarm.py" ]