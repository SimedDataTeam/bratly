FROM ubuntu:jammy

RUN apt-get update

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN uv python install 3.10 3.11 3.12
RUN uv tool install toml-cli

ENV PATH="/root/.local/bin:${PATH}"
ENV UV_LINK_MODE=copy
ENV UV_NATIVE_TLS=true
