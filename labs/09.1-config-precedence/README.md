# Lab 9.1: Configuration precedence and visibility

**Module M09 · Configuration: environment variables, build args and config files** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** Observe ENV defaults, runtime overrides, env files and ARG behaviour, and see exactly where values are visible.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`m09/Dockerfile`](m09/Dockerfile) → copied to `~/labs/m09/Dockerfile`
- [`m09/app.conf`](m09/app.conf) → copied to `~/labs/m09/app.conf`
- [`m09/app.env`](m09/app.env) → copied to `~/labs/m09/app.env`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/m09 && cp -a ~/shikumi-docker-labs/labs/09.1-config-precedence/m09/. ~/labs/m09/
ls -A ~/labs/m09
```

### Step 1: Build a small image with an ARG and an ENV (Dockerfile copied in step 0).

```bash
mkdir -p ~/labs/m09 && cd ~/labs/m09
cat Dockerfile
docker build --build-arg BUILD_NOTE=ci-run-42 -t cfgdemo .
```

### Step 2: Run with image defaults, then override.

```bash
docker run --rm cfgdemo
docker run --rm -e GREETING="from cli" cfgdemo
```

### Step 3: Use the env file (app.env, copied in step 0); then combine with -e (later wins).

```bash
docker run --rm --env-file app.env cfgdemo
docker run --rm --env-file app.env -e LOG_LEVEL=warn cfgdemo
```

### Step 4: Where are values visible?

```bash
docker run -d --name cfg -e API_KEY=not-a-secret cfgdemo sleep 60
docker inspect --format '{{json .Config.Env}}' cfg
docker history --no-trunc cfgdemo | grep -o 'BUILD_NOTE=ci-run-42' | head -1
```

### Step 5: Inject a config file (app.conf, copied in step 0) read-only instead of baking it in.

```bash
docker run --rm -v "$PWD/app.conf:/etc/app/app.conf:ro" alpine:3.24 cat /etc/app/app.conf
```

## Checks (expected output)

- Default run prints 'GREETING=from image LOG_LEVEL=info BUILD_NOTE=unset' and 'build note was: ci-run-42'
- -e GREETING overrides only GREETING
- --env-file sets both; adding -e LOG_LEVEL=warn after it wins
- docker inspect shows API_KEY=not-a-secret in plain text
- docker history --no-trunc reveals BUILD_NOTE=ci-run-42
- The mounted config file prints feature_x=true

## Stretch challenge

What does '-e GREETING' (no value) do when GREETING is unset in your shell, and when you have run 'export GREETING=sneaky' first? Test both and explain.

## Cleanup

```bash
docker rm -f cfg
docker image rm cfgdemo
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). ARG value visible in docker history --no-trunc; -e value visible in docker inspect.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
