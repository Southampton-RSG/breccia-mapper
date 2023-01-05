FROM python:3.9-slim

RUN groupadd -r mapper && useradd --no-log-init -r -g mapper mapper

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt gunicorn

COPY . ./

# USER mapper

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD [ "gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "breccia_mapper.wsgi" ]
