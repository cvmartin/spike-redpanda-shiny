FROM python:3.11


COPY ./ ./

RUN pip install --no-cache-dir --upgrade "."

RUN adduser --system --no-create-home shiny

USER shiny

EXPOSE 3838

CMD ["python", "./docker_deploy/shiny_app/entrypoint.py"]
