# FinTrack Infrastructure

## Assignment Details

**Assignment:** Assignment #2 — Release Night Chaos: Stabilizing Hypergrowth Infra
**Name:** Jayashree
**Repository:** `fintrack-infra`
**GitHub:** `jayashree3349-ops/fintrack-infra`

---

## 1. Problem Statement

FinTrack experienced a production release-night incident involving multiple reliability, deployment, CI/CD, Kubernetes, traffic-management, monitoring, and security problems.

The incident included:

* A canary deployment accidentally reaching 100% traffic.
* Failed canary releases and unreliable rollback behavior.
* Kubernetes pods entering `CrashLoopBackOff`, `ImagePullBackOff`, `Pending`, and `OOMKilled` states.
* Jenkins builds and agents becoming unreliable.
* Pull requests being merged without sufficient approval controls.
* Prometheus metrics/alerting gaps.
* Kubernetes resource pressure.
* Configuration that could cause users to reach the new version directly.
* Docker image tag mismatches during rollback.
* Risk of secrets being committed to source control.

The objective was to stabilize the platform while improving release safety, CI/CD reliability, Kubernetes resilience, traffic control, governance, and observability.

---

## 2. Solution Overview

The FinTrack environment was stabilized using:

* Git and GitHub branch/PR governance.
* Jenkins CI/CD with immutable commit-based image tags.
* Dockerized account-service application.
* Kubernetes Deployments, Services, health probes, resource limits, and ResourceQuota.
* Istio DestinationRule and VirtualService for controlled canary traffic.
* Automatic Jenkins rollback when a deployment fails.
* GitHub Actions PR validation.
* Prometheus-compatible alert definitions.
* Chaos testing for common Kubernetes failure modes.
* Security and repository hygiene checks.

The final release is tagged:

`v2025.06.2`

---

## 3. Repository Structure

```text
fintrack-infra/
├── .github/
│   └── workflows/
│       └── pr-checks.yml
├── config/
│   └── application.env
├── docker/
│   └── account-service/
│       ├── Dockerfile
│       └── app/
│           └── server.py
├── k8s/
│   └── base/
│       ├── namespace.yaml
│       ├── resource-quota.yaml
│       ├── account-service-v1.yaml
│       ├── account-service-v2.yaml
│       ├── account-service-service.yaml
│       ├── account-service-destination-rule.yaml
│       ├── account-service-virtual-service.yaml
│       └── kustomization.yaml
├── monitoring/
│   ├── README.md
│   └── prometheus/
│       ├── fintrack-alert-rules.yaml
│       └── canary-alerts.yaml
├── Jenkinsfile
├── README.md
└── .gitignore
```

---

## 4. Architecture

### Application

The `account-service` application exposes:

* `/health` — application health endpoint.
* `/version` — returns the active application version.

Two Kubernetes versions are deployed:

* `account-service-v1`
* `account-service-v2`

### Kubernetes

The application runs in the `fintrack` namespace.

Kubernetes resources include:

* Namespace
* Deployments
* ClusterIP Service
* ResourceQuota
* Resource requests and limits
* Liveness/readiness health checks

### Istio

Istio provides version-based traffic routing.

The final canary configuration is:

```text
v1 → 90%
v2 → 10%
```

A `DestinationRule` defines the v1 and v2 subsets, while the `VirtualService` controls the traffic weights.

---

## 5. CI/CD

### Jenkins

The Jenkins pipeline performs:

1. Source checkout.
2. Application validation.
3. Docker image build.
4. Docker Hub push.
5. Capture of the currently deployed image.
6. Kubernetes deployment.
7. Rollout verification.
8. Deployment availability verification.
9. Istio configuration verification.
10. Automatic rollback when deployment verification fails.

Images are tagged using the Git commit SHA instead of mutable release tags.

Example:

```text
dina98942/fintrack-account-service:<git-commit>
```

This provides traceability between source code, Docker image, and Kubernetes deployment.

### Automatic Rollback

Before deploying a new image, Jenkins captures the currently deployed image.

If the rollout fails:

```text
Deployment failure
       ↓
Capture failure
       ↓
Restore previous image
       ↓
Wait for rollout
       ↓
Verify restored image
```

The rollback mechanism was tested using an intentionally unavailable image. The failed release triggered automatic rollback and restored the previous working image.

---

## 6. GitHub Actions

The repository contains:

```text
.github/workflows/pr-checks.yml
```

The workflow validates:

* YAML syntax.
* Prometheus alert definitions.
* Kustomize rendering.
* Application source files.
* Docker image build.
* Container health endpoint.
* Container version endpoint.

Pull requests are protected using GitHub rules requiring review and CI validation.

---

## 7. Resource Management

The Kubernetes namespace uses a ResourceQuota.

Configured quota:

```text
CPU requests:       1
Memory requests:    2Gi
CPU limits:         4
Memory limits:      3Gi
Pods:               20
```

Application containers use explicit CPU and memory requests/limits.

This prevents uncontrolled resource consumption and provides predictable scheduling behavior.

The lab also demonstrated Kubernetes scheduling failure when available memory was insufficient.

---

## 8. Monitoring and Alerting

Prometheus-compatible rules were added for:

* Deployment availability.
* CrashLoopBackOff.
* OOMKilled containers.
* Image pull failures.
* High CPU usage.
* High memory usage.
* Canary HTTP 5xx errors.
* Canary latency.

The Minikube lab environment did not contain a running Prometheus/Alertmanager stack, so live alert firing was not claimed.

The alert definitions are structured for integration with a production Prometheus deployment.

---

## 9. Security and Governance

Repository protections include:

* Pull request requirement.
* Required approval before merge.
* Required CI validation.
* Force-push protection.
* Branch deletion protection.

Repository secret checks were performed.

No actual hardcoded secret values were identified in the tracked configuration.

Docker registry credentials are referenced through Jenkins credentials rather than hardcoded into the pipeline.

The repository also contains `.gitignore` protections for secret files.

The Jenkins lab environment uses Docker-in-Docker with an unauthenticated Docker API for the local challenge environment. This should not be reproduced in production without appropriate TLS/authentication and isolation.

---

## 10. Chaos Testing

The following failure scenarios were reproduced and investigated:

| Scenario                              | Result                   |
| ------------------------------------- | ------------------------ |
| ImagePullBackOff                      | Passed                   |
| CrashLoopBackOff                      | Passed                   |
| OOMKilled                             | Passed                   |
| Pending due to insufficient resources | Passed                   |
| Failed Kubernetes rollout             | Passed                   |
| Automatic Jenkins rollback            | Passed                   |
| Accidental 100% canary                | Reproduced and corrected |
| 90/10 canary restoration              | Verified                 |

The final canary verification produced:

```text
93 account-service:v1
 7 account-service:v2
```

for 100 requests, which is consistent with the configured 90/10 probabilistic routing.

---

## 11. Final Kubernetes Verification

The final application state was:

```text
account-service-v1   1/1 Available
account-service-v2   1/1 Available
```

Both application pods were healthy with:

```text
2/2 Running
0 restarts
```

The final Istio routing configuration was:

```text
v1 = 90%
v2 = 10%
```

Kustomize rendering completed successfully.

---

## 12. Validation

The final release was verified with:

```bash
kubectl kustomize k8s/base
```

and Git reported:

```text
nothing to commit, working tree clean
```

The release tag is:

```text
v2025.06.2
```

The repository contains the Docker, Kubernetes, Jenkins, monitoring, and GitHub Actions implementation.

---

## 13. Setup Requirements

The following tools are required for the lab:

* Git
* Docker
* kubectl
* Kubernetes cluster
* Minikube or equivalent Kubernetes environment
* Istio / istioctl
* Jenkins
* GitHub repository
* Python 3 for application/validation tooling

Optional production integrations:

* Docker Hub or another container registry.
* Prometheus.
* Alertmanager.
* Grafana.
* External secret management.

---

## 14. Deployment Steps

### Clone

```bash
git clone https://github.com/jayashree3349-ops/fintrack-infra.git
cd fintrack-infra
```

### Validate Kustomize

```bash
kubectl kustomize k8s/base
```

### Deploy Kubernetes resources

```bash
kubectl apply -k k8s/base
```

### Verify deployments

```bash
kubectl get pods -n fintrack
kubectl get deployments -n fintrack
```

### Verify Istio

```bash
kubectl get virtualservice -n fintrack
kubectl get destinationrule -n fintrack
```

### Verify rollout

```bash
kubectl rollout status deployment/account-service-v1 -n fintrack
kubectl rollout status deployment/account-service-v2 -n fintrack
```

---

## 15. Release

Current release:

```text
v2025.06.2
```

The release contains the integrated FinTrack infrastructure implementation on the `main` branch.

---

## 16. Conclusion

The FinTrack release-night environment was stabilized by combining controlled Istio canary routing, Kubernetes resource governance, health checks, reliable Jenkins deployment automation, automatic rollback, GitHub PR governance, CI validation, monitoring definitions, and chaos testing.

The final state provides a safer deployment workflow in which releases are traceable, canaries are explicitly controlled, failed deployments can automatically recover, and changes are validated before reaching protected branches.

