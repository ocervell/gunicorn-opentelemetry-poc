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
from werkzeug.exceptions import default_exceptions
import time
import random
from helpers import instrument
CHAOS_TARGET_PERCENT = int(os.environ.get('CHAOS_TARGET_PERCENT', '0'))
CHAOS_ERROR_CODES = list(default_exceptions.keys())

# Flask application
app = Flask(__name__)
app_tags = [
    'app:flask-app', 'service:flask-app', 'env:staging', 'version:1.0.0'
]

# Logging setup
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route("/")
@instrument('flask_app_hello_requests', app_tags)
def hello():
    start = time.time()
    app.logger.info('Received hello request !')
    app.logger.debug('Counter was incremented.')
    if CHAOS_TARGET_PERCENT != 0:
        percent = random.randint(0, 100)
        if percent <= CHAOS_TARGET_PERCENT:
            status_code = random.choice(CHAOS_ERROR_CODES)
            abort(status_code)
    return 'Hello World!'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
