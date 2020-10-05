# Gunicorn (Flask) demo application

This repository is a POC application to demonstrate instrumenting a `gunicorn`
application running on Google Kubernetes engine.

## Architectures
Different branches correspond to different telemetry setup in order to accommodate different environments:

| Description                                                            | Branch                        |
|------------------------------------------------------------------------|-------------------------------|
| OpenTelemetry Collector (Tier 1 setup)                                 | [arch/otel-agent][]           |  
| OpenTelemetry Collector (Tier 2 setup)                                 | [arch/otel-agent-collector][] |
| OpenTelemetry SDK + Cloud Monitoring exporter                          | [arch/otel-sdk-cloudops][]    |
| Prometheus SDK + Stackdriver Prometheus Sidecar + Cloud Trace exporter | [arch/prometheus][]           |

[arch/otel-agent]: https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/otel-agent
[arch/otel-agent-collector]: https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/otel-agent-collector
[arch/otel-sdk-cloudops]: https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/otel-sdk-cloudops
[arch/prometheus]: https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/prometheus
[feature/datadog]: https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/feature/datadog [alpha]
