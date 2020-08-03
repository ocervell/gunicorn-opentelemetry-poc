# Gunicorn Flask application with OpenTelemetry instrumentation

This repository is a POC application to demonstrate OpenTelemetry instrumentation for a gunicorn application running on GKE, including framework metrics and traces as well as custom metrics and traces.

The metrics backend configured in this repository is Cloud Monitoring (ex Stackdriver), but modifying it should be straightforward to adapt this example to other metrics or trace backends.

This branch deploys an agentless setup using the OpenTelemetry SDK:

-   **OpenTelemetry SDK (Python)** is used to send traces directly to Cloud Monitoring and expose custom metrics to a Prometheus exporter.
-   **Prometheus** and `prometheus-to-sd` are deployed to scrape metrics from Prometheus exporters.
-   **OpenTelemetry collector is NOT deployed.**

The architecture is as below:

![](architecture.png)

## Installation

The installation steps below assumes you already have a running GKE cluster.

### Deploy the custom-metrics-example

    cd custom-metrics-example
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT_ID>/custom-metrics-example:latest .
    kubectl apply -f app.yaml

### Build and deploy the gunicorn application

    cd flask-app
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT_ID>/flask-app:latest .
    kubectl apply -f app.yaml

### Deploy Prometheus and patch it with prometheus-to-sd

    cd ops/prometheus/
    kubectl apply -f prometheus.yaml

Set the required variables in `.env` file, then:

    source .env
    ./patch.sh

### Deploy the loadtester

    cd loadtester
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT>/loadtester:latest
    kubectl apply -f k8s/locust_master_controller.yaml
    kubectl apply -f k8s/locust_master_service.yaml

Set the `LOCUST_MASTER` env variable in `k8s/locust_worker_controller.yaml` and apply it:

    kubectl apply -f k8s/locust_worker_controller.yaml
