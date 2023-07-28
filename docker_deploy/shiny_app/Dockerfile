FROM python:3.11

RUN adduser --system --no-create-home shiny

COPY ./ ./

RUN pip install --no-cache-dir --upgrade "."

USER shiny

EXPOSE 3838

CMD ["python3", "./docker_deploy/shiny_app/entrypoint.py"]
