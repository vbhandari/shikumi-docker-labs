# Lab 13.4: Scan the course image

**Module M13 · Security** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** Find HIGH/CRITICAL vulnerabilities in the API image with a pinned Trivy that never touches the Docker socket, and compare base images.

## Before you start

- Lab 5.2 (image `myapi:2.0`)
- Optional: a Docker account for the Docker Scout step
- Run the steps in order, in the same terminal, unless a step says otherwise.

If you skipped the earlier lab, run this first:

```bash
docker image inspect myapi:2.0 >/dev/null 2>&1 || { mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/05.2-multi-stage-build/app/. ~/labs/app/ && docker build -t myapi:2.0 ~/labs/app; }
```

## Steps

### Step 1: Save the image to a tarball and scan it with a digest-pinned Trivy.

```bash
mkdir -p ~/labs/m13 && cd ~/labs/m13
docker image save myapi:2.0 -o myapi.tar
docker volume create trivy-cache
TRIVY_SHA=2416d1f74045b57274df1a340eee6b510cacd73c66a6ccb8da092b117eb7d222
TRIVY="aquasec/trivy:0.76.0@sha256:$TRIVY_SHA"
docker run --rm -v "$PWD":/work:ro -v trivy-cache:/root/.cache "$TRIVY" image --input /work/myapi.tar --severity HIGH,CRITICAL --no-progress 2>&1 | tail -25
```

### Step 2: Compare with the full python base image.

```bash
docker image save python:3.14 -o py-full.tar 2>/dev/null || (docker pull -q python:3.14 && docker image save python:3.14 -o py-full.tar)
TRIVY_SHA=2416d1f74045b57274df1a340eee6b510cacd73c66a6ccb8da092b117eb7d222
TRIVY="aquasec/trivy:0.76.0@sha256:$TRIVY_SHA"
docker run --rm -v "$PWD":/work:ro -v trivy-cache:/root/.cache "$TRIVY" image --input /work/py-full.tar --severity HIGH,CRITICAL --no-progress --format table 2>&1 | grep -E '^(Total|Report Summary)|python:3.14|py-full' | head -8
```

### Step 3: Optional, with a Docker account: Docker Scout.

*Optional: install the Docker Scout CLI plugin first:*

<!-- verify: skip -->
```bash
curl -fsSL https://raw.githubusercontent.com/docker/scout-cli/c7ac4ce317eafa536bf2421d1c223908e2200dce/install.sh -o install-scout.sh
# Read install-scout.sh before you run it
sh install-scout.sh v1.26.0
docker scout version
```

*Run alone, then follow the prompt:*

<!-- verify: skip -->
```bash
docker login
```

*After you have signed in:*

<!-- verify: skip -->
```bash
docker scout quickview myapi:2.0
docker scout cves --only-severity critical,high myapi:2.0
docker scout recommendations myapi:2.0
```

## Checks (expected output)

- Trivy downloads its DB into the trivy-cache volume on first run, then prints a report for myapi.tar (debian 13 OS packages + Python packages)
- The slim multi-stage image reports few findings (typically in pip/setuptools tooling); the full python:3.14 image reports hundreds of OS-package findings
- docker scout version reports v1.26.0; Scout quickview prints a summary of vulnerabilities by severity and base-image recommendations

## Stretch challenge

Add '--exit-code 1 --severity CRITICAL' to the Trivy command and use it as a CI gate in a shell script that blocks 'docker push' when it fails.

## Cleanup

```bash
rm -f ~/labs/m13/*.tar
docker image rm python:3.14
```

## Tested

Partially verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Trivy 0.76.0 (digest-pinned) scanned saved tarballs. The pinned Docker Scout installer (v1.26.0) was run and docker scout version checked; the Scout scan steps were not run because they need a Docker account.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
