# Copyright 2020 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import config
import os
import requests
import logging
import time
from flask import Flask
from opentelemetry import trace, metrics
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.ext.opencensusexporter.metrics_exporter import OpenCensusMetricsExporter
from opentelemetry.ext.opencensusexporter.trace_exporter import OpenCensusSpanExporter
OTEL_AGENT_ENDPOINT = os.environ['OTEL_AGENT_ENDPOINT']
span_exporter = OpenCensusSpanExporter(service_name="flask-app-tutorial",
                                       endpoint=OTEL_AGENT_ENDPOINT)
exporter = OpenCensusMetricsExporter(service_name="flask-app-tutorial",
                                     endpoint=OTEL_AGENT_ENDPOINT)

# Metrics
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__, True)
metrics.get_meter_provider().start_pipeline(meter, exporter, 5)

# Traces
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(span_exporter))

# Custom metrics
pid = os.getpid()
staging_labels = {"environment": "staging", "pid": str(pid)}
requests_counter = meter.create_metric(
    name="hello_requests_otagent",
    description="Hello requests count",
    unit="1",
    value_type=int,
    metric_type=Counter,
    label_keys=(
        "environment",
        "pid",
    ),
)

# Flask application
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# Logging setup
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
app.logger.info(f'Otel agent endpoint: {OTEL_AGENT_ENDPOINT}')


@app.route("/")
def hello():
    app.logger.info("Received hello request !")
    requests_counter.add(1, staging_labels)
    app.logger.debug("Counter was incremented.")
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
