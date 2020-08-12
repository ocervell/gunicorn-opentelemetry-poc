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
"""
This example shows how to export metrics to the OT collector.
"""
import os
import time

from opentelemetry import metrics
from opentelemetry.exporter.opencensus.metrics_exporter import (
    OpenCensusMetricsExporter, )
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.resources import get_aggregated_resources
from gke_detector import GoogleCloudResourceDetector

OTEL_AGENT_ENDPOINT = os.environ['OTEL_AGENT_ENDPOINT']
exporter = OpenCensusMetricsExporter(service_name="custom-metrics-example",
                                     endpoint=OTEL_AGENT_ENDPOINT)
resource = get_aggregated_resources([GoogleCloudResourceDetector()])

metrics.set_meter_provider(MeterProvider(resource=resource))
meter = metrics.get_meter(__name__)
metrics.get_meter_provider().start_pipeline(meter, exporter, 10)

custom_metric_example = meter.create_metric(
    name="custom_metric_example",
    description="Example of custom metric sent with OC exporter",
    unit="1",
    value_type=int,
    metric_type=Counter)

metric_labels = {'app': 'custom-metrics-example', 'environment': 'staging'}
while (True):
    time.sleep(5)
    custom_metric_example.add(1, metric_labels)
    print('Custom metric incremented.')
