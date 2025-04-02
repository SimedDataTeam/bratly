FROM mcr.microsoft.com/devcontainers/base:jammy

USER 1000

USER root

# RUN rm /usr/bin/python3 && rm /usr/bin/python3.10

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN mkdir -p /workspaces/plumbing
RUN chown 1000:1000 /workspaces/plumbing

USER 1000

RUN uv python install 3.10 3.11 3.12
RUN echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc

RUN uv tool install ruff

RUN uv tool install toml-cli

# RUN uv venv /workspaces/plumbing/venv
ENV UV_PROJECT_ENVIRONMENT=/workspaces/project/.venv

ENV RUFF_CACHE_DIR=/workspace/plumbing/.cache/ruff
ENV MYPY_CACHE_DIR=/workspace/plumbing/.cache/mypy
ENV PRE_COMMIT_HOME=/workspace/plumbing/.cache/pre-commit

ENV UV_LINK_MODE=copy
ENV UV_NATIVE_TLS=true

COPY --chown=1000:1000 ./bratly/dockerfiles/ruff.pyproject.toml /home/vscode/.config/ruff/pyproject.toml

COPY --chown=1000:1000 ./bratly/dockerfiles/zsh_additions /home/vscode/zsh_additions
RUN echo '\n\n#Adding all files from zsh_additions\nfor f in ~/zsh_additions/*.zsh; do source "$f"; done' >> /home/vscode/.zshrc

USER root
 