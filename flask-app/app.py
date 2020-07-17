import config
import requests
from flask import Flask
from opentelemetry import trace, metrics
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics.export.controller import PushController

# Method 1: Export to OT collector
#from opentelemetry.ext.opencensusexporter.metrics_exporter import OpenCensusMetricsExporter
#from opentelemetry.ext.opencensusexporter.trace_exporter import OpenCensusSpanExporter
#span_exporter = OpenCensusSpanExporter(service_name="basic-service", endpoint="localhost:55678")
#exporter = OpenCensusMetricsExporter(
#    service_name="basic-service", endpoint="localhost:55678")

# Method 2: Export to Cloud Ops
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
span_exporter = CloudTraceSpanExporter()
exporter = CloudMonitoringMetricsExporter()


# Metrics
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__, True)
controller = PushController(meter, exporter, 5)



# Traces
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(span_exporter))

# Custom metrics
staging_labels = {"environment": "staging"}
requests_counter = meter.create_metric(
    name="hello",
    description="number of hello requests",
    unit="1",
    value_type=int,
    metric_type=Counter,
    label_keys=("environment",),
)

# Flask application
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route("/")
def hello():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("example-request"):
        requests.get("http://www.example.com")
    requests_counter.add(1, staging_labels)
    return "Hello World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
