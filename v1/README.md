## Datadog.Trace Debugging

1. `DD_API_KEY=abcdefg docker compose up -d dd-agent`
1. `docker compose up --build -d control-healthcheck`
1. `docker compose up --build -d control-idle`
1. `docker compose up --build -d metrics-healthcheck`
1. `docker compose up --build -d metrics-idle`
1. `docker compose up --build -d nometrics-healthcheck`
1. `docker compose up --build -d nometrics-idle`