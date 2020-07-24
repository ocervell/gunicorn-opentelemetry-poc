# Gunicorn Flask application with OpenTelemetry instrumentation

This repository is a POC application to demonstrate OpenTelemetry instrumentation for a gunicorn application running on GKE, including framework metrics and traces as well as custom metrics and traces.

The metrics backend configured in this repository is Cloud Monitoring (ex Stackdriver), but modifying it should be straightforward to adapt this example to other metrics or trace backends.

This branch deploys an agentless setup using the OpenTelemetry SDK:

-   Custom metrics are directly sent to Cloud Trace / Cloud Monitoring from the application code, using the corresponding OpenTelemetry SDK exporters.
-   OT agent / collector deployments are not deployed.
-   Prometheus / `prometheus-to-sd` are deployed.

The architecture is as below:

![](architecture.png)

## Installation

The installation steps below assume you already have a running GKE cluster.

### Build and deploy the gunicorn application

    cd flask-app
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT_ID>/flask-app:<VERSION> .

Update the version of the app in the `app.yaml`, and then deploy the app to your GKE cluster:

    kubectl apply -f app.yaml

### Deploy Prometheus and patch it with prometheus-to-sd

    cd ops/prometheus/full
    # follow instructions in the README.md

### Deploy the loadtester

    cd loadtester
    gcloud builds submit --tag=gcr.io/<YOUR_PROJECT>/loadtester:<VERSION> .
    kubectl apply -f k8s/locust_master_controller.yaml
    kubectl apply -f k8s/locust_master_service.yaml

Set the `LOCUST_MASTER` env variable in `k8s/locust_worker_controller.yaml` and apply it:

    kubectl apply -f k8s/locust_worker_controller.yaml
