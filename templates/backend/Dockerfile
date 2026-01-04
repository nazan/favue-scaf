FROM python:3.11.4

ARG USER_ID
ARG GROUP_ID

RUN apt-get update && apt-get install -y \
    --no-install-recommends

RUN (groupadd -g $GROUP_ID appuser 2>/dev/null || groupmod -n appuser $(getent group $GROUP_ID | cut -d: -f1)) && \
    (useradd -m -u $USER_ID -g $GROUP_ID appuser 2>/dev/null || usermod -l appuser -d /home/appuser -m $(getent passwd $USER_ID | cut -d: -f1))

USER appuser

RUN mkdir /home/appuser/venv

ENV VIRTUAL_ENV=/home/appuser/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV && pip install --upgrade pip

RUN mkdir /home/appuser/app
WORKDIR /home/appuser/app

