FROM python:3.8-slim

# NOTE: From https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
RUN groupadd -r python && \
	useradd --no-log-init -m -g python python

# Install requirements
ARG REQUIREMENTS_FILE=requirements-ci.txt
COPY ${REQUIREMENTS_FILE} /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

USER python
WORKDIR /home/python
