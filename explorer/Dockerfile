FROM python:3.8.0
EXPOSE 8000
ADD . /home/user/explorer
WORKDIR /home/user/explorer
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "/bin/sh", "entrypoint.sh"]