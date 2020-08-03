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
from flask import Flask
from opentelemetry import trace, metrics
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

span_exporter = CloudTraceSpanExporter()

# Traces
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(span_exporter))

# Flask application
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
metrics = GunicornPrometheusMetrics(app)

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
requests_counter = metrics.counter('flask_app_hello_requests',
                                   'Hello requests count',
                                   labels=metric_labels)

# Logging setup
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route("/")
@requests_counter
def hello():
    app.logger.info('Received hello request !')
    app.logger.debug('Counter was incremented.')
    return 'Hello World!'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
