FROM python:3.13-bookworm

RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    jq \
    ripgrep \
    fd-find \
    tree \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv


WORKDIR /workspace