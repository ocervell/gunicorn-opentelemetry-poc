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

import os

from functools import wraps
from time import time
from flask import request

from datadog import initialize, statsd, util

STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost')
STATSD_PORT = int(os.environ.get('STATSD_PORT', '8125'))
initialize({'statsd_host': STATSD_HOST, 'statsd_port': STATSD_PORT})


def instrument(metric, tags=[]):
    """
    A decorator that instruments a Flask HTTP request.

    Args:
        metric (str): Metric name
        tags (list): List of tags to add to metric.

    Returns:
        func: Decorated function.
    """
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            start = time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                result = e
                raise e
            finally:
                if isinstance(result, str):  # string response, 200
                    status_code = 200
                else:
                    status_code = result.code
                status_code_class = str(int(status_code / 100)) + 'xx'
                http_tags = [
                    f'http.status_code:{status_code}',
                    f'http.status_code_class:{status_code_class}',
                    f'http.path:{request.path}',
                    f'http.method:{request.method}',
                ]
                req_tags = tags.copy()
                req_tags.extend(http_tags)
                print(req_tags)
                latency = (time() - start) * 1000
                statsd.distribution(f'{metric}.latency.distribution',
                                    latency,
                                    tags=req_tags)
                statsd.increment(f'{metric}.count', tags=req_tags)
            return result

        return wrapped

    return wrapper
