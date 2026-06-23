FROM python:3.14

WORKDIR /darkatlas

COPY requirements.txt /darkatlas/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /darkatlas/requirements.txt

COPY ./backend /darkatlas/backend
COPY alembic.ini /darkatlas/alembic.ini
COPY pytest.ini /darkatlas/pytest.ini

COPY ./backend/entrypoint.sh /darkatlas/entrypoint.sh
RUN chmod +x /darkatlas/entrypoint.sh

CMD ["/darkatlas/entrypoint.sh"]