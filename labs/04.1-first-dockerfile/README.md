# Lab 4.1: Build, run and inspect the API

**Module M04 · Dockerfile fundamentals** · about 25 min · [Lab index](../../README.md#lab-index)

**Goal:** Create the project files, build the image, run it with runtime configuration and verify the response.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`app/.dockerignore`](app/.dockerignore) → copied to `~/labs/app/.dockerignore`
- [`app/Dockerfile`](app/Dockerfile) → copied to `~/labs/app/Dockerfile`
- [`app/app.py`](app/app.py) → copied to `~/labs/app/app.py`
- [`app/requirements.txt`](app/requirements.txt) → copied to `~/labs/app/requirements.txt`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/04.1-first-dockerfile/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Look at the project files you just copied (app.py, requirements.txt, Dockerfile, .dockerignore).

```bash
mkdir -p ~/labs/app && cd ~/labs/app
cat Dockerfile
ls -la
```

### Step 2: Build and tag the image.

```bash
docker build -t myapi:v1 .
```

### Step 3: Run it with a published loopback port and an env var.

```bash
docker run -d --name api -p 127.0.0.1:5000:5000 -e GREETING="built in M04" myapi:v1
sleep 2
curl -sS http://127.0.0.1:5000/
```

### Step 4: Check logs, the environment and the image metadata.

```bash
docker logs --tail 5 api
docker exec api printenv GREETING
docker image inspect --format '{{json .Config.Cmd}} {{json .Config.ExposedPorts}}' myapi:v1
```

### Step 5: Override CMD at run time to prove it is only a default.

```bash
docker run --rm myapi:v1 python -c 'import importlib.metadata as m; print(m.version("flask"))'
```

## Checks (expected output)

- ls -la shows app.py, requirements.txt, Dockerfile, .dockerignore
- The build finishes with 'naming to docker.io/library/myapi:v1'
- curl returns JSON with "message":"hello v1" and "greeting":"built in M04"
- docker logs shows the Flask dev-server banner ('* Running on all addresses (0.0.0.0)') and a '"GET / HTTP/1.1" 200' line
- printenv prints 'built in M04'; Cmd is ["python","app.py"], ExposedPorts {"5000/tcp":{}}
- The override prints 3.1.3

## Stretch challenge

Add 'ARG APP_VERSION=dev' and 'LABEL org.opencontainers.image.version=$APP_VERSION' to the Dockerfile, build with --build-arg APP_VERSION=1.0.0 and read it back with docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' myapi:v1.

## Cleanup

```bash
docker rm -f api
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Flask 3.1.3 installed. pip warns about running as root; the M05 virtualenv + non-root image fixes that.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
