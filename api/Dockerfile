FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8 as build-image

COPY ./requirements.txt ./

RUN pip wheel --wheel-dir=/root/wheels -r requirements.txt

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8 as production-image

COPY --from=build-image /root/wheels /root/wheels

COPY --from=build-image /app/requirements.txt ./

RUN echo "Acquire::Check-Valid-Until \"false\";\nAcquire::Check-Date \"false\";" | cat > /etc/apt/apt.conf.d/10no--check-valid-until

RUN apt-get -y update
RUN apt-get -y install libgl1-mesa-glx dos2unix

RUN pip install --no-index --find-links=/root/wheels -r requirements.txt

LABEL org.opencontainers.image.source="https://github.com/YacineJazi/imdb-fast-api-jazi-yacine"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app:app --reload"]

CMD ["uvicorn", "app.app:app", "8000"]

COPY ./app /app
ENV PYTHONPATH=/app