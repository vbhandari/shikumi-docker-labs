# Lab 16.1: Kubernetes-readiness audit of the course image

**Module M16 · Bridge to Kubernetes** · about 30 min · [Lab index](../../README.md#lab-index)

**Goal:** Check the capstone image against a Kubernetes readiness checklist using only Docker tools, and record the evidence a Pod spec will need.

## Before you start

- Lab 15.1 (image `localhost:5001/shikumi-api:3.0.0` pushed to the local registry)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`app/.dockerignore`](app/.dockerignore) → copied to `~/labs/app/.dockerignore`
- [`app/Dockerfile`](app/Dockerfile) → copied to `~/labs/app/Dockerfile`
- [`app/app.py`](app/app.py) → copied to `~/labs/app/app.py`
- [`app/compose.prod.yaml`](app/compose.prod.yaml) → copied to `~/labs/app/compose.prod.yaml`
- [`app/compose.yaml`](app/compose.yaml) → copied to `~/labs/app/compose.yaml`
- [`app/requirements.txt`](app/requirements.txt) → copied to `~/labs/app/requirements.txt`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/16.1-kubernetes-readiness/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Install jq (used in step 9; skip if already installed in Lab 12.1).

<!-- verify: skip -->
```bash
sudo apt-get install -y jq
```

### Step 2: Runs as a fixed non-root UID (needed for runAsNonRoot / runAsUser).

```bash
docker image inspect --format 'user={{.Config.User}}' localhost:5001/shikumi-api:3.0.0
```

### Step 3: Health endpoints exist and answer fast (future readiness/liveness probes).

```bash
cd ~/labs/app && docker compose -f compose.prod.yaml up -d --wait
docker compose -f compose.prod.yaml exec api python -c "import urllib.request,time; t=time.time(); print(urllib.request.urlopen('http://127.0.0.1:5000/healthz').read(), round(time.time()-t,3),'s')"
```

### Step 4: Handles SIGTERM promptly (Kubernetes sends SIGTERM then waits terminationGracePeriodSeconds, default 30 s).

```bash
time docker compose -f compose.prod.yaml stop api
docker compose -f compose.prod.yaml start api
```

### Step 5: Works with a read-only root and no capabilities (securityContext).

```bash
docker inspect --format 'ro={{.HostConfig.ReadonlyRootfs}} capdrop={{.HostConfig.CapDrop}}' shikumi-prod-api-1
```

### Step 6: Logs go to stdout/stderr (kubectl logs reads the same streams).

```bash
docker compose -f compose.prod.yaml logs --tail 3 api
```

### Step 7: Config comes from env and files only: list what a ConfigMap and Secret must provide.

```bash
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' shikumi-prod-api-1 | grep -E '^(REDIS_HOST|MESSAGE)='
docker compose -f compose.prod.yaml exec api ls /run/secrets
```

### Step 8: Reference the image by digest, as a Pod spec should.

```bash
docker buildx imagetools inspect localhost:5001/shikumi-api:3.0.0 --format '{{json .Manifest.Digest}}'
```

### Step 9: Generate a starting point for manifests: the fully resolved Compose model.

```bash
docker compose -f compose.prod.yaml config --format json | jq '.services.api | {image, environment, healthcheck, deploy, user, read_only, cap_drop}'
```

## Checks (expected output)

- user=10001
- healthz returns b'{"status":"ok"}\n' in a few milliseconds
- stop completes in about a second, well under 30 s
- ro=true capdrop=[ALL]
- Recent gunicorn access/info lines appear in logs
- REDIS_HOST=redis and MESSAGE=hello from production listed; /run/secrets contains api_token
- A sha256 digest is printed
- jq prints the api service's image, environment, healthcheck, resource limits, user, read_only and cap_drop

## Stretch challenge

Using the audit output and the concept map, write (on paper or in a text file - no cluster needed) the fields of a Deployment and Service for the API: image@digest, replicas, env from ConfigMap, Secret volume at /run/secrets, readiness and liveness probes on /healthz, requests/limits, securityContext. Bring it to the Kubernetes course.

## Cleanup

```bash
cd ~/labs/app && docker compose -f compose.prod.yaml down
docker rm -f registry   # optional: end of course
docker compose down   # dev stack from M10
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). All audit checks produced evidence (user 10001, healthz in ~17 ms, sub-second SIGTERM stop, ro root, digest, resolved Compose model).

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
