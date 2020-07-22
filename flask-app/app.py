import config
import os
import requests
import logging
import time
from flask import Flask
from opentelemetry import trace, metrics
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
span_exporter = CloudTraceSpanExporter()
exporter = CloudMonitoringMetricsExporter(add_unique_identifier=True)

# Metrics
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__, True)
metrics.get_meter_provider().start_pipeline(meter, exporter, 1)

# Traces
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(span_exporter))

# Custom metrics
staging_labels = {"environment": "staging"}
requests_counter = meter.create_metric(
    name="hello_requests_otagent",
    description="Hello requests count",
    unit="1",
    value_type=int,
    metric_type=Counter,
    label_keys=("environment", ),
)

# Flask application
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Logging setup
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route("/")
def hello():
    app.logger.info("Received hello request !")
    requests_counter.add(1, staging_labels)
    app.logger.debug("Counter was incremented.")
    time.sleep(1)
    requests.get('https://www.google.com')
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
