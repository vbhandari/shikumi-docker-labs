# Lab 10.1: API + Redis with Compose

**Module M10 · Docker Compose** · about 30 min · [Lab index](../../README.md#lab-index)

**Goal:** Run the two-service app, observe startup order, service-name DNS and persistence, and use the Compose lifecycle commands.

## Before you start

- Lab 5.2 (this lab reuses the multi-stage Dockerfile, included here)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`app/.dockerignore`](app/.dockerignore) → copied to `~/labs/app/.dockerignore`
- [`app/Dockerfile`](app/Dockerfile) → copied to `~/labs/app/Dockerfile`
- [`app/app.py`](app/app.py) → copied to `~/labs/app/app.py`
- [`app/compose.yaml`](app/compose.yaml) → copied to `~/labs/app/compose.yaml`
- [`app/requirements.txt`](app/requirements.txt) → copied to `~/labs/app/requirements.txt`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/10.1-compose-api-redis/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Look at app v3, its requirements and compose.yaml (copied in step 0), then validate the file.

```bash
cd ~/labs/app
cat compose.yaml
docker compose config --quiet && echo "compose.yaml is valid"
```

### Step 2: Build and start, waiting for health.

```bash
docker compose up -d --build --wait
docker compose ps
```

### Step 3: Call the API a few times; the counter lives in Redis.

```bash
for i in 1 2 3; do curl -sS http://127.0.0.1:8000/; echo; done
```

### Step 4: Logs, exec and service DNS.

```bash
docker compose logs --tail 5 api
docker compose exec redis redis-cli get hits
docker compose exec api python -c "import socket; print(socket.gethostbyname('redis'))"
docker network ls --filter label=com.docker.compose.project=shikumi
```

### Step 5: Persistence: recreate everything except the volume.

```bash
docker compose down
docker volume ls --filter name=shikumi_redis-data
docker compose up -d --wait
curl -sS http://127.0.0.1:8000/; echo
```

### Step 6: Change config with an interpolated variable.

```bash
GREETING='hi from the shell' docker compose up -d --wait
curl -sS http://127.0.0.1:8000/; echo
```

## Checks (expected output)

- 'compose.yaml is valid' is printed
- up --wait returns once both services are running/healthy; compose ps shows shikumi-api-1 and shikumi-redis-1 (redis 'healthy')
- hits increases 1, 2, 3
- redis-cli get hits prints "3"; gethostbyname('redis') prints a 172.x address; network shikumi_default exists
- After down/up the volume shikumi_redis-data still exists and hits continues at 4
- The greeting changes to 'hi from the shell' (Compose recreated only the api container)

## Stretch challenge

Scale the API: remove the fixed host port, add a second service 'proxy' (nginx:stable) that publishes 127.0.0.1:8000:80 and proxies to http://api:5000, then 'docker compose up -d --scale api=3'. Watch the hostname of responses change.

## Cleanup

```bash
# leave the stack running for Lab 10.2
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Compose v5.6.0: up --wait, service DNS, volume persistence across down/up (hits continued at 4) and interpolation all confirmed.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
