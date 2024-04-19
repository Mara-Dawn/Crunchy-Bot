# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12

# Get Rust; NOTE: using sh for better compatibility with other base images
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain 1.77.2 -y

# Add .cargo/bin to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Check cargo is visible
RUN cargo --help


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