# FinTrack Monitoring and Alerting

## Environment finding

The supplied Minikube environment was inspected for:

- Prometheus
- Alertmanager
- Grafana
- Metrics Server
- Prometheus Operator CRDs
- ServiceMonitor
- PrometheusRule

None were installed in the challenge cluster.

Therefore, live alert firing could not be demonstrated without introducing
an additional monitoring platform.

## Alert coverage

The repository contains Prometheus-compatible alert definitions covering:

- Deployment unavailable
- CrashLoop/repeated container restarts
- OOMKilled
- ImagePullBackOff / ErrImagePull
- High CPU
- High memory
- Canary v2 5xx error rate
- Canary v2 latency

## Canary protection

The canary alerts specifically monitor the Istio v2 subset.

The intended production workflow is:

1. Deploy a small percentage of traffic to v2.
2. Monitor v2 error rate and latency.
3. Alert when thresholds are exceeded.
4. Stop promotion or automatically rollback the deployment.
5. Restore the previous known-good image.

## Lab limitation

The current Minikube environment does not provide the Prometheus,
Alertmanager, or Kubernetes metrics APIs required for live evaluation.

The alert definitions are therefore maintained as version-controlled
deployment artifacts and should be loaded into the organization's
Prometheus/Alertmanager stack in a production environment.
