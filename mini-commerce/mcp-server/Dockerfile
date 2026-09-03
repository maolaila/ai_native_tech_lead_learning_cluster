FROM python:3.13-slim
RUN useradd --system --uid 10001 app
WORKDIR /app
COPY pyproject.toml ./
COPY src src
RUN pip install --no-cache-dir .
USER 10001
EXPOSE 8081
ENTRYPOINT ["mini-commerce-mcp"]
