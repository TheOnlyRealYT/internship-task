FROM python:3.14

WORKDIR /darkatlas

COPY ./backend/requirements.txt /darkatlas/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /darkatlas/requirements.txt

COPY ./backend /darkatlas/app

CMD ["fastapi", "run", "app/app.py", "--port", "80"]