FROM jenkins/jenkins:2.541.3-lts-jdk17

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io docker-cli git \
    && rm -rf /var/lib/apt/lists/*
USER jenkins
