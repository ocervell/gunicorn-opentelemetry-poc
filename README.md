# Gunicorn Flask application with OpenTelemetry instrumentation

This repository is a POC application to demonstrate OpenTelemetry instrumentation for a `gunicorn` application running on Google Kubernetes engine.

In this design:

-   `gunicorn` is configured to forward framework metrics to a Prometheus `statsd-exporter` (sidecar container).

-   `OpenTelemetry` agent is deployed as a `daemonset` and configured with:

    -   An OpenCensus `receiver` to receive the application custom metrics sent via the SDK.


-   `OpenTelemetry` collector is deployed as a `deployment` to achieve the two-tier architecture, and configured with:

    -   A Prometheus `receiver` to scrape Prometheus exporters metrics (drop-in replacement for a full-fledged Prometheus instance).

    -   An OpenCensus `receiver` to receive the metrics from the agent.

    -   A `Cloud Trace` and `Cloud Monitoring` `exporter` to ship metrics and traces to Cloud Operations.


-   `OpenTelemetry SDK` for Python is used within the app and `OpenCensusMetricsExporter` and `OpenCensusSpanExporter` are configured to export custom metrics and spans to the OpenTelemetry agent.

-   `Prometheus` and `prometheus-to-sd` are not used.

The architecture is as follows:

![](architecture.png)

## Installation

The installation steps below assume you already have a running GKE cluster.

### Deploy the OpenTelemetry agent and collector

    cd ops/opentelemetry
    kubectl apply -f ot-agent.yaml
    kubectl apply -f ot-collector.yaml

To change the configuration of the agent, refer to the configuration [documentation](https://opentelemetry.io/docs/collector/configuration/) and edit the `ot-agent.yaml`' or `ot-collector.yaml` `ConfigMap` resource.

### Deploy the custom-metrics-example

    cd custom-metrics-example
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT_ID>/custom-metrics-example:latest .
    kubectl apply -f app.yaml

### Build and deploy the gunicorn application

    cd flask-app
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT_ID>/flask-app:latest .
    kubectl apply -f app.yaml

### Deploy the loadtester

    cd loadtester
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT>/loadtester:latest
    kubectl apply -f k8s/locust_master_controller.yaml
    kubectl apply -f k8s/locust_master_service.yaml

Set the `LOCUST_MASTER` env variable in `k8s/locust_worker_controller.yaml` and apply it:

    kubectl apply -f k8s/locust_worker_controller.yaml
