FROM python
ARG ACCESS_TOKEN
ARG OMDB_API_KEY
ARG FIREBASE_URL
COPY chatbot.py ./
COPY requirements.txt ./
COPY firebase-adminsdk.json ./
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=$ACCESS_TOKEN
ENV OMDB_API_KEY=$OMDB_API_KEY
ENV FIREBASE_URL=$FIREBASE_URL
cmd python chatbot.py