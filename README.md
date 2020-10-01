# Gunicorn (Flask) demo application

This repository is a POC application to demonstrate instrumenting a `gunicorn`
application running on Google Kubernetes engine.

## Architectures
Different branches correspond to different telemetry setup in order to accommodate different environments:

### [OpenTelemetry Collector (Tier 1 setup)](https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/otel-agent)

  * [`gunicorn`][] application exporting framework metrics to `statsd-exporter`


  * [`Flask`][] app configured with:
    * [`opentelemetry-python`][] SDK for custom metrics and traces
    * [`opentelemetry-instrumentation-flask`][] for Flask framework integration (traces)
    * [`opentelemetry-exporter-opencensus`][] to export metrics and traces to the OT collector


  * [`opentelemetry-collector-contrib`][] deployed as a `daemonset`, and configured with:
    * [`prometheusreceiver`][] to scrape `statsd-exporter` Gunicorn metrics
    * [`opencensusreceiver`][] to scrape custom app metrics
    * [`stackdriverexporter`][] to export metrics and traces to Cloud Operations API

### [OpenTelemetry Collector (Tier 2 setup)](https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/otel-agent-collector)

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

### [OpenTelemetry SDK + Cloud Monitoring exporter](https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/otel-sdk-cloudops)

  * [`gunicorn`][] application exporting framework metrics to `statsd-exporter`


  * [`Flask`][] app configured with:
    * [`opentelemetry-python`][] SDK for custom metrics and traces
    * [`opentelemetry-instrumentation-flask`][] for Flask framework integration (traces)
    * [`opentelemetry-exporter-cloud-monitoring`][] to export metrics directly to Cloud Monitoring API
    * [`opentelemetry-exporter-cloud-trace`][] to export traces directly to Cloud Trace API

### [Prometheus SDK + Stackdriver Prometheus Sidecar + Cloud Trace exporter](https://github.com/ocervell/gunicorn-opentelemetry-poc/tree/arch/prometheus)

  * [`gunicorn`][] application not exporting framework metrics


  * [`Flask`][] app configured with:
    * [`prometheus-flask-exporter`][] to expose Gunicorn metrics (multiprocessed) as a Prometheus scrape target
    * [`opentelemetry-exporter-google-cloud`][] to export traces directly to Cloud Monitoring API


  * [`Prometheus`][] configured with:
    * Configuration to scrape metrics from containers if k8s metric port name matches `*-metrics`.
    * Sidecar `stackdriver-prometheus-sidecar` to convert and export metrics to Cloud Monitoring API.



[`Flask`]: https://github.com/pallets/flask
[`gunicorn`]: https://github.com/benoitc/gunicorn
[`Prometheus`]: https://github.com/prometheus/prometheus
[`opentelemetry-python`]: https://github.com/open-telemetry/opentelemetry-python
[`opentelemetry-instrumentation-flask`]: https://github.com/open-telemetry/opentelemetry-python/tree/master/instrumentation/opentelemetry-instrumentation-flask
[`opentelemetry-collector-contrib`]: https://github.com/open-telemetry/opentelemetry-collector-contrib
[`opentelemetry-exporter-google-cloud`]: https://github.com/GoogleCloudPlatform/opentelemetry-operations-python/tree/master/opentelemetry-exporter-google-cloud
[`opentelemetry-exporter-cloud-monitoring`]: https://pypi.org/project/opentelemetry-exporter-cloud-monitoring/
[`opentelemetry-exporter-cloud-trace`]: https://pypi.org/project/opentelemetry-exporter-cloud-trace/
[`opentelemetry-exporter-opencensus`]: https://github.com/open-telemetry/opentelemetry-python/tree/master/exporter/opentelemetry-exporter-opencensus
[`prometheus-flask-exporter`]: https://github.com/rycus86/prometheus_flask_exporter
[`opencensusreceiver`]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/opencensusreceiver
[`opencensusexporter`]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/exporter/opencensusexporter
[`prometheusreceiver`]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/prometheusreceiver
[`stackdriverexporter`]: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/master/exporter/stackdriverexporter
