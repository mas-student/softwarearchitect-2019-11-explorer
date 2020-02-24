FROM python:3.8.0
EXPOSE 8000
ADD . /home/user/loader
WORKDIR /home/user/loader
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["/bin/sh", "entrypoint.sh"]