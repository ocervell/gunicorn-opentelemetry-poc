#!/bin/sh

set -e
set -u

kubectl -n "${KUBE_NAMESPACE}" patch deployment/prometheus-k8s -n kube-system --type strategic --patch "
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
        ports:
        - name: sidecar
          containerPort: 9091
        volumeMounts:
        - name: data-volume
          mountPath: /data
"
