# Gunicorn Flask application with OpenTelemetry instrumentation

This repository is a POC application to demonstrate OpenTelemetry instrumentation for a gunicorn application running on GKE, including framework metrics and traces as well as custom metrics and traces.

The metrics backend configured in this repository is Cloud Monitoring (ex Stackdriver), but modifying it should be straightforward to adapt this example to other metrics or trace backends.

This branch deploys a Prometheus-based monitoring setup:

-   **[OpenTelemetry SDK (Python)](https://github.com/open-telemetry/opentelemetry-python)** is used to send traces directly to Cloud Monitoring.
-   **[Prometheus Flask exporter](https://github.com/rycus86/prometheus_flask_exporter)** is used to expose framework (gunicorn) metrics and custom metrics as a Prometheus scrape endpoint.
-   **[Prometheus](https://prometheus.io/)** and **[stackdriver-prometheus-sidecar](https://github.com/Stackdriver/stackdriver-prometheus-sidecar)** are deployed to scrape metrics from Prometheus exporters.
-   **OpenTelemetry collector is NOT deployed.**
-   **statsd-exporter is NOT deployed** because the Prometheus Flask exporter supports gunicorn multiprocessed setup.

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
    kubectl apply -f service.yaml

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

### Observe the metrics in Cloud Monitoring

The metrics deployed by this setup in Cloud Monitoring should match the following types:

    external.googleapis.com/prometheus/custom_metric_example
    external.googleapis.com/prometheus/flask_app_hello_requests
    external.googleapis.com/prometheus/flask_exporter_info
    external.googleapis.com/prometheus/flask_http_request
    external.googleapis.com/prometheus/flask_http_request_duration_seconds
    external.googleapis.com/prometheus/process_cpu_seconds
    external.googleapis.com/prometheus/process_max_fds
    external.googleapis.com/prometheus/process_open_fds
    external.googleapis.com/prometheus/process_resident_memory_bytes
    external.googleapis.com/prometheus/process_start_time_seconds
    external.googleapis.com/prometheus/process_virtual_memory_bytes
    external.googleapis.com/prometheus/python_gc_collections
    external.googleapis.com/prometheus/python_gc_objects_collected
    external.googleapis.com/prometheus/python_gc_objects_uncollectable
    external.googleapis.com/prometheus/python_info
    external.googleapis.com/prometheus/scrape_duration_seconds
    external.googleapis.com/prometheus/scrape_samples_post_metric_relabeling
    external.googleapis.com/prometheus/scrape_samples_scraped
    external.googleapis.com/prometheus/up
