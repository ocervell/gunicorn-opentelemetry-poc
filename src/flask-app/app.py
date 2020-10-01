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
import logging
import time
import pprint
import random
from flask import Flask, abort
from opentelemetry import trace, metrics
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
CHAOS_TARGET_PERCENT = int(os.environ.get('CHAOS_TARGET_PERCENT', '0'))
span_exporter = CloudTraceSpanExporter()
exporter = CloudMonitoringMetricsExporter(add_unique_identifier=True)

# Metrics
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__, True)
metrics.get_meter_provider().start_pipeline(meter, exporter, 5)

# Traces
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(span_exporter))

# Custom metrics
metric_labels = {
    'app': 'flask-app',
    'environment': 'staging',
    'kubernetes_container_name': os.getenv('CONTAINER_NAME'),
    'kubernetes_namespace': os.getenv('NAMESPACE'),
    'kubernetes_pod_name': os.getenv('POD_NAME'),
    'kubernetes_pod_ip': os.getenv('POD_IP'),
    'kubernetes_host_ip': os.getenv('OTEL_AGENT_HOST')
}
requests_counter = meter.create_metric(
    name='flask_app_hello_requests',
    description='Hello requests count',
    unit='1',
    value_type=int,
    metric_type=Counter,
    label_keys=tuple(metric_labels.keys()),
)
requests_latency = meter.create_metric(name="flask_app_hello_latency",
                                       description="Hello requests latency",
                                       unit="ms",
                                       value_type=float,
                                       metric_type=ValueRecorder)

# Flask application
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# Logging setup
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route("/")
def hello():
    start = time.time()
    app.logger.info('Received hello request !')
    requests_counter.add(1, metric_labels)
    app.logger.debug('Counter was incremented.')
    if CHAOS_TARGET_PERCENT != 0:
        percent = random.randint(0, 100)
        if percent <= CHAOS_TARGET_PERCENT:
            status_code = random.randint(400, 500)
            latency = (time.time() - start) * 1000
            metric_latency_labels['http.status_code'] = str(status_code)
            requests_latency.record(latency, metric_latency_labels)
            abort(status_code)
    latency = (time.time() - start) * 1000
    metric_latency_labels['http.status_code'] = str(200)
    requests_latency.record(latency, metric_latency_labels)
    return 'Hello World!'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
