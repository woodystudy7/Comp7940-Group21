FROM python
COPY chatbot.py ./
COPY requirements.txt ./
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=5204041470:AAE7zYk1cLAybz_HMscUuw0Xusju6IhkZ4o
CMD python chatbot.py