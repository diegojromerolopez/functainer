ARG FROM_IMAGE=python:3.10
FROM $FROM_IMAGE
ARG REQUIREMENTS
RUN if [ -n "$REQUIREMENTS" ]; then pip install $REQUIREMENTS; fi

RUN useradd functainer_user
USER functainer_user
WORKDIR /home/functainer_user
