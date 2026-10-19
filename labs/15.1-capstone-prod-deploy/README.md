# Lab 15.1: Capstone: deploy the hardened stack from the registry

**Module M15 · Production practices and capstone** · about 45 min · [Lab index](../../README.md#lab-index)

**Goal:** Build, tag and push v3.0.0, deploy the production stack from the registry, and verify health, limits, secrets, isolation, logs and restart behaviour.

## Before you start

- Lab 6.1 (local registry on 127.0.0.1:5001; step 1 restarts it if needed)
- Lab 13.3 (`~/labs/app/secrets/api_token.txt`; if missing, recreate it with the command under Prerequisites)
- Run the steps in order, in the same terminal, unless a step says otherwise.

If you skipped the earlier lab, run this first:

```bash
cd ~/labs/app && [ -f secrets/api_token.txt ] || { mkdir -p secrets && printf 'shikumi-admin-%s' "$(date +%s)" > secrets/api_token.txt && chmod 644 secrets/api_token.txt; }
```

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
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/15.1-capstone-prod-deploy/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Make sure the registry from M06 is running and the token file from M13 exists.

```bash
docker start registry >/dev/null 2>&1 || docker run -d --name registry --restart unless-stopped -p 127.0.0.1:5001:5000 -v registry-data:/var/lib/registry registry:3
cd ~/labs/app && ls secrets/api_token.txt
```

### Step 2: Look at compose.prod.yaml (copied in step 0), then build and push the image.

```bash
cd ~/labs/app
grep -nE 'image:|read_only|cap_drop|limits|internal' compose.prod.yaml
docker compose -f compose.prod.yaml build
docker compose -f compose.prod.yaml push api
curl -sS http://127.0.0.1:5001/v2/shikumi-api/tags/list
```

### Step 3: Remove the local copy and deploy from the registry.

```bash
docker image rm localhost:5001/shikumi-api:3.0.0
docker compose -f compose.prod.yaml up -d --wait --pull always --no-build
docker compose -f compose.prod.yaml ps
```

### Step 4: Functional checks.

```bash
curl -sS http://127.0.0.1:8090/; echo
curl -sS -H "X-Admin-Token: $(cat secrets/api_token.txt)" http://127.0.0.1:8090/admin; echo
```

### Step 5: Hardening and limits are really applied.

```bash
docker inspect --format 'mem={{.HostConfig.Memory}} cpu={{.HostConfig.NanoCpus}} pids={{.HostConfig.PidsLimit}} ro={{.HostConfig.ReadonlyRootfs}} init={{.HostConfig.Init}} log={{.HostConfig.LogConfig.Type}}' shikumi-prod-api-1
docker compose -f compose.prod.yaml exec api id
```

### Step 6: Isolation: Redis is on an internal network with no route out, and isn't published.

```bash
docker compose -f compose.prod.yaml port redis 6379 ; echo "(no published port)"
docker network inspect --format '{{.Name}} internal={{.Internal}}' shikumi-prod_backend
```

### Step 7: Resilience: simulate a crash by killing the container's init process from the host, and watch it come back.

```bash
sudo kill -9 $(docker inspect --format '{{.State.Pid}}' shikumi-prod-api-1)
sleep 25
docker inspect --format 'restarts={{.RestartCount}} health={{.State.Health.Status}}' shikumi-prod-api-1
```

### Step 8: Graceful stop is fast (init forwards SIGTERM to gunicorn).

```bash
time docker compose -f compose.prod.yaml stop api
docker compose -f compose.prod.yaml start api
```

## Checks (expected output)

- compose push lists the layers pushed without errors; tags/list includes 3.0.0 next to the M06 tags
- up --pull always pulls the API image from the registry and returns once both services are healthy
- curl returns message 'hello from production' with an increasing hits counter; /admin with the token returns admin ok
- inspect prints mem=268435456 cpu=500000000 pids=100 ro=true init=true log=local; id prints uid=10001
- compose port prints ':0' for redis (no published port); backend network shows internal=true
- After the crash the restart policy brings the API back: restarts=1, health=healthy
- docker compose stop api completes in well under the 20 s grace period

## Stretch challenge

Pin redis by digest: resolve it with 'docker buildx imagetools inspect redis:8.8-alpine', write image: redis:8.8-alpine@sha256:..., and redeploy. Then add a 'backup' profile service that tars the redis-data volume nightly into ./backups.

## Cleanup

```bash
docker compose -f compose.prod.yaml down   # keep the volume; add -v to delete data
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Deployed from the local registry with --pull always --no-build. Limits, read-only root, init and the local log driver were applied. A host-side kill -9 of the init PID triggered the restart (restarts=1, healthy). Graceful stop took ~0.7 s.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
