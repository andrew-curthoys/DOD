FROM continuumio/miniconda3

WORKDIR /bot

COPY /bot/keys.py .
COPY /dick_or_don.db .

COPY /bot/environment.yml .
RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "dod", "/bin/bash", "-c"]

COPY /bot/daily_dod.py .
ENTRYPOINT ["conda", "run", "-n", "dod", "python", "daily_dod_docker.py"]
