# Gunicorn Flask application with OpenTelemetry instrumentation

This repository is a POC application to demonstrate OpenTelemetry instrumentation for a `gunicorn` application running on Google Kubernetes engine.

In this design:

-   `gunicorn` is configured to forward framework metrics to a Prometheus `statsd-exporter` (sidecar container).

-   `OpenTelemetry` agent is deployed as a `daemonset` and configured with:

    -   A Prometheus `receiver` to scrape the `statsd-exporter` metrics (drop-in replacement for a full-fledged Prometheus instance).

    -   An OpenCensus `receiver` to receive the application custom metrics sent via the SDK.

    -   A `Cloud Trace` and `Cloud Monitoring` `exporter` to ship metrics and traces to Cloud Operations.

-   `OpenTelemetry SDK` for Python is used within the app and `OpenCensusMetricsExporter` and `OpenCensusSpanExporter` are configured to export custom metrics and spans to the OpenTelemetry agent.

-   `Prometheus` and `prometheus-to-sd` are not used.

The architecture is as follows:

![](architecture.png)

## Installation

To deploy the services, run:

    skaffold run --default-repo=gcr.io/<PROJECT_ID> -p gcb

where &lt;PROJECT_ID> is the project that will run the Cloud Build jobs.

The above command deploys the following services:

| Service                                                | Language       | Description                                                                                                                                    |
| ------------------------------------------------------ | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| [custom-metrics-example](./src/custom-metrics-example) | Python         | Generates a custom metric named 'custom-metrics-example'                                                                                       |
| [flask-app](./src/flask-app)                           | Python (Flask) | Simple Flask application with a single endpoint '/' instrumentized (metrics and traces) with the Flask extension for OpenTelemetry Python SDK. |
| [loadtester](./src/loadtester)                         | Python         | Locust master / workers that generate a load on the Flask application in order to get frequent metric / trace writes.                          |
