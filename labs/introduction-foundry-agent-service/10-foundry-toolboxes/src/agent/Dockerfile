# Hosted agent image for acl-remedy-advisor-hosted, toolbox edition (Module 10).
# Foundry runs this container, sends OpenAI Responses requests on port 8088, and
# probes /readiness automatically. Build for linux/amd64.
FROM python:3.13-slim

WORKDIR /app

COPY . user_agent/
WORKDIR /app/user_agent

RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        echo "No requirements.txt found"; \
    fi

EXPOSE 8088

CMD ["python", "main.py"]
