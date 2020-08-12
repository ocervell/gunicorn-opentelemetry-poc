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
from opentelemetry.sdk.metrics import Counter, MeterProvider
from prometheus_client import start_http_server, Counter

custom_metric_example = Counter(
    'custom_metric_example',
    'Example of custom metric sent with Prometheus client',
    ['app', 'environment'],
)
metric_labels = {'app': 'custom-metrics-example', 'environment': 'staging'}
start_http_server(9090)
while (True):
    time.sleep(5)
    custom_metric_example.labels(**metric_labels).inc()
    print('Custom metric incremented.')
