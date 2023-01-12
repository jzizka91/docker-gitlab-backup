FROM python:latest

WORKDIR /opt/gitlab-backup

ENV GROUPID=<default-group-id>
ENV BACKUPDIR=/backup

# Copy requirements files
COPY requirements.txt daily-backup.py ./

# Install all requirements
RUN apt-get update && apt-get install -y git-lfs && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir --upgrade -r requirements.txt

CMD [ "python3", "-u", "./daily-backup.py" ]