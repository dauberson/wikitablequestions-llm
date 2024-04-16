FROM python:3.11.5

ARG APP_DIR=/home
WORKDIR ${APP_DIR}
ARG AUTHED_ARTIFACT_REG_URL

COPY entrypoint.sh  /home
COPY wikitablequestions-llm-service/main/wikitablequestions_llm_service/main.py /home/wikitablequestions-llm-service/main/wikitablequestions_llm_service/main.py

RUN apt-get update \
    && apt-get clean \
    && apt-get install -y build-essential

RUN pip install --upgrade pip \
    && pip install --extra-index-url ${AUTHED_ARTIFACT_REG_URL} wikitablequestions-llm

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]