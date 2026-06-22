FROM python:3.14

WORKDIR /darkatlas

COPY requirements.txt /darkatlas/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /darkatlas/requirements.txt

COPY ./backend /darkatlas/backend

CMD ["fastapi", "run", "backend/app.py", "--port", "80"]