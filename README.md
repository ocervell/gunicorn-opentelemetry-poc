# Gunicorn (Flask) demo app
### Instrumentation: Prometheus SDK + Prometheus + Cloud Monitoring

The architecture is as below:

![](architecture.png)

**Architecture details:**

* [`gunicorn`][] application not exporting framework metrics


* [`Flask`][] app configured with:
  * [`prometheus-flask-exporter`][] to expose Gunicorn metrics (multiprocessed) as a Prometheus scrape target
  * [`opentelemetry-exporter-google-cloud`][] to export traces directly to Cloud Monitoring API


* [`Prometheus`][] configured with:
  * Configuration to scrape metrics from containers if k8s metric port name matches `*-metrics`.
  * Sidecar `stackdriver-prometheus-sidecar` to convert and export metrics to Cloud Monitoring API.

## Installation

### Create a GKE Cluster

Enable the container API:

```sh
gcloud services enable container.googleapis.com
```

Create a GKE cluster:

```sh
gcloud container clusters create <CLUSTER_NAME> \
  --enable-autoupgrade \
  --enable-autoscaling --min-nodes=3 --max-nodes=10 --num-nodes=5 \
  --zone=<ZONE>
```

Verify that the cluster is up-and-running:

```sh
kubectl get nodes
```

### Enable Google Container Registry

Enable Google Container Registry (GCR) on your GCP project:

```sh
gcloud services enable containerregistry.googleapis.com
```

and configure the `docker` CLI to authenticate to GCR:

```sh
gcloud auth configure-docker -q
```

## Create Datadog secret
```
kubectl create secret generic datadog-agent --from-literal api-key="<DATADOG_API_KEY>" --namespace="default"
```

### Build and deploy everything

Install skaffold and run:

    skaffold run --default-repo=gcr.io/[PROJECT_ID]

where [PROJECT_ID] is your GCP project ID where you will push container images to.

This command:

-   builds the container images
-   pushes them to GCR
-   applies the `./kubernetes-manifests` deploying the application to
    Kubernetes.

**Troubleshooting:** If you get "No space left on device" error on Google
Cloud Shell, you can build the images on Google Cloud Build: [Enable the
Cloud Build
API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com),
then run `skaffold run -p gcb --default-repo=gcr.io/[PROJECT_ID]` instead.


### Patch Prometheus with prometheus-to-sd

    cd k8s/
    kubectl apply -f prometheus.yaml

Set the required variables in `.env` file, then:

    source .env
    ./prometheus_patch.sh

### Observe the results

Find the IP address of your application, then visit the application on your browser to confirm installation.

    kubectl get service flask-app-tutorial

**Troubleshooting:** A Kubernetes bug (will be fixed in 1.12) combined with
a Skaffold [bug](https://github.com/GoogleContainerTools/skaffold/issues/887)
causes load balancer to not to work even after getting an IP address. If you
are seeing this, run `kubectl get service flask-app-tutorial -o=yaml | kubectl apply -f-`
to trigger load balancer reconfiguration.

The above command deploys the following services:

| Service                                                | Language       | Description                                                                                                                                    |
| ------------------------------------------------------ | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| [custom-metrics-example](./src/custom-metrics-example) | Python         | Generates a custom metric named 'custom-metrics-example'                                                                                       |
| [flask-app](./src/flask-app)                           | Python (Flask) | Simple Flask application with a single endpoint '/' instrumentized (metrics and traces) with the Flask extension for OpenTelemetry Python SDK. |
| [loadtester](./src/loadtester)                         | Python         | Locust master / workers that generate a load on the Flask application in order to get frequent metric / trace writes.                          |

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


[`Flask`]: https://github.com/pallets/flask
[`gunicorn`]: https://github.com/benoitc/gunicorn
[`Prometheus`]: https://github.com/prometheus/prometheus
[`opentelemetry-exporter-google-cloud`]: https://github.com/GoogleCloudPlatform/opentelemetry-operations-python/tree/master/opentelemetry-exporter-google-cloud
[`prometheus-flask-exporter`]: https://github.com/rycus86/prometheus_flask_exporter
[`opencensusreceiver`]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/opencensusreceiver
