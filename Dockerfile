FROM python
COPY chatbot.py ./
COPY requirements.txt ./
COPY firebase-adminsdk.json ./
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=5204041470:AAE7zYk1cLAybz_HMscUuw0Xusju6IhkZ4o
ENV OMDB_API_KEY=1bd45b7f
ENV FIREBASE_URL=https://test-44b3a-default-rtdb.firebaseio.com/
RUN python chatbot.py