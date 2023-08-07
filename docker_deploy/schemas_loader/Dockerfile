FROM python:3.11


RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/*

CMD ["bash", "./etc/schemas_loader/entrypoint.sh"]
