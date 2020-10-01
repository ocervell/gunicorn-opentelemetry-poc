# Gunicorn (Flask) demo application
#### Instrumentation: OT SDK + OT Agent (Daemonset) + OT Agent (Deployment) + Cloud Monitoring

The architecture is as follows:

![](architecture.png)

**Architecture details:**
* [`gunicorn`][] application exporting framework metrics to `statsd-exporter`


* [`Flask`][] app configured with:
  * [`opentelemetry-python`][] SDK for custom metrics and traces
  * [`opentelemetry-instrumentation-flask`][] for Flask framework integration (traces)
  * [`opentelemetry-exporter-opencensus`][] to export metrics and traces to the OT collector


* [`opentelemetry-collector-contrib`][] deployed as a `daemonset`, and configured with:
  * [`prometheusreceiver`][] to scrape `statsd-exporter` Gunicorn metrics
  * [`opencensusreceiver`][] to scrape custom app metrics
  * [`opencensusexporter`][] to export metrics and traces to OpenTelemetry deployment)


* [`opentelemetry-collector-contrib`][] deployed as a `deployment`, and configured with:
  * [`opencensusreceiver`][] to receive metrics from the daemonset
  * [`stackdriverexporter`][] to export metrics and traces to Cloud Operations API

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

[`Flask`]: https://github.com/pallets/flask
[`gunicorn`]: https://github.com/benoitc/gunicorn
[`opentelemetry-python`]: https://github.com/open-telemetry/opentelemetry-python
[`opentelemetry-instrumentation-flask`]: https://github.com/open-telemetry/opentelemetry-python/tree/master/instrumentation/opentelemetry-instrumentation-flask
[`opentelemetry-collector-contrib`]: https://github.com/open-telemetry/opentelemetry-collector-contrib
[`opentelemetry-exporter-opencensus`]: https://github.com/open-telemetry/opentelemetry-python/tree/master/exporter/opentelemetry-exporter-opencensus
[`opencensusreceiver`]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/opencensusreceiver
[`opencensusexporter`]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/exporter/opencensusexporter
[`prometheusreceiver`]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/prometheusreceiver
[`stackdriverexporter`]: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/master/exporter/stackdriverexporter
