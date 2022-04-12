FROM python
COPY chatbot.py ./
COPY requirements.txt ./
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=5164413606:AAEehwH8tSaQJhh4i0jntGlUF35guu1lWBo
CMD python chatbot.py