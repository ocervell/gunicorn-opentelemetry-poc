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
#!/bin/sh

set -e
set -u

kubectl -n "${KUBE_NAMESPACE}" patch deployment/prometheus-k8s --type strategic --patch "
spec:
  template:
    spec:
      containers:
      - name: stackdriver-prometheus-sidecar
        image: gcr.io/stackdriver-prometheus/stackdriver-prometheus-sidecar:${SIDECAR_IMAGE_TAG}
        imagePullPolicy: Always
        args:
        - --stackdriver.project-id=${GCP_PROJECT}
        - --prometheus.wal-directory=/data/wal
        - --stackdriver.kubernetes.location=${GCP_REGION}
        - --stackdriver.kubernetes.cluster-name=${KUBE_CLUSTER}
        -  --include={job=~'kubernetes-pods'}
        ports:
        - name: sidecar
          containerPort: 9091
        volumeMounts:
        - name: data-volume
          mountPath: /data
"
