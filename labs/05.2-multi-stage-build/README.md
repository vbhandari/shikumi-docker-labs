# Lab 5.2: Multi-stage build with targets

**Module M05 · Build cache, multi-stage builds and BuildKit / Buildx** · about 25 min · [Lab index](../../README.md#lab-index)

**Goal:** Build test and runtime targets from one Dockerfile, run the hardened image and measure the result honestly.

## Before you start

- Lab 5.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`app/.dockerignore`](app/.dockerignore) → copied to `~/labs/app/.dockerignore`
- [`app/Dockerfile`](app/Dockerfile) → copied to `~/labs/app/Dockerfile`
- [`app/Dockerfile.fat`](app/Dockerfile.fat) → copied to `~/labs/app/Dockerfile.fat`
- [`app/app.py`](app/app.py) → copied to `~/labs/app/app.py`
- [`app/requirements.txt`](app/requirements.txt) → copied to `~/labs/app/requirements.txt`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/05.2-multi-stage-build/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Look at the multi-stage Dockerfile and the new requirements (Flask + gunicorn) you copied.

```bash
cd ~/labs/app
cat requirements.txt
cat Dockerfile
```

### Step 2: Build only the test stage; it must print 'import ok'.

```bash
docker build --target test --progress=plain -t myapi:test . 2>&1 | grep 'import ok'
```

### Step 3: Build the runtime image (the last stage is the default target).

```bash
docker build -t myapi:2.0 .
```

### Step 4: Run it and check user, server and health.

```bash
docker run -d --name api -p 127.0.0.1:5000:5000 myapi:2.0
sleep 15
curl -sS http://127.0.0.1:5000/
docker exec api id
docker logs api 2>&1 | head -3
docker inspect --format '{{.State.Health.Status}}' api
```

### Step 5: Compare sizes against a single-stage build on the full python image (Dockerfile.fat, copied in step 0).

```bash
docker build -f Dockerfile.fat -t myapi:fat .
docker image ls myapi --format 'table {{.Tag}}\t{{.Size}}'
```

## Checks (expected output)

- The test-stage build prints 'import ok'
- curl returns hello v2 JSON from gunicorn
- docker exec api id prints uid=10001(appuser) gid=10001(appuser)
- logs start with '[INFO] Starting gunicorn 26.2.0' and 'Listening at: http://0.0.0.0:5000'
- Health status is 'healthy' after the first interval
- myapi:fat is several times larger than myapi:2.0; myapi:2.0 is only slightly larger than myapi:v2 (gunicorn + venv)

## Stretch challenge

Add a 'dev' stage that installs pytest and runs with Flask's reloader, and build it with --target dev. Which stage should CI build first, and why?

## Cleanup

```bash
docker rm -f api
docker image rm myapi:fat myapi:test
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Sizes on the build machine: myapi:fat 1.64GB, myapi:2.0 207MB, myapi:v2 201MB. Health reached 'healthy'. id = uid=10001(appuser).

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
