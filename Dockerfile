
FROM apache/airflow:3.1.0

USER root


# RUN apt-get update && apt-get install -y --no-install-recommends \
#     package-name-1 \
#     package-name-2 \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*


USER airflow


COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt
