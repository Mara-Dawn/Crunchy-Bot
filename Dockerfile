# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt


WORKDIR /app
COPY . /app


RUN git init .
RUN pre-commit install-hooks
RUN rm -rf .git

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# ENTRYPOINT ["python", "src/main.py"]
CMD python src/main.py