# Lab 2.2: Drive a container through every state

**Module M02 · The container lifecycle** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** Create, start, pause, stop, kill and remove containers, and measure how PID 1 signal handling changes docker stop.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: Create without starting, then start.

```bash
docker create --name life alpine:3.24 sleep 300
docker ps -a --filter name=life --format '{{.Names}} {{.Status}}'
docker start life
docker ps --filter name=life --format '{{.Names}} {{.Status}}'
```

### Step 2: Pause and unpause; the process is frozen, not stopped.

```bash
docker pause life
docker inspect --format '{{.State.Status}}' life
docker unpause life
```

### Step 3: Time a normal stop. sleep as PID 1 ignores SIGTERM, so Docker waits for the timeout.

```bash
time docker stop life
docker inspect --format 'exit={{.State.ExitCode}}' life
```

### Step 4: Repeat with --init: tini forwards SIGTERM and sleep exits at once.

```bash
docker run -d --init --name life-init alpine:3.24 sleep 300
time docker stop life-init
docker inspect --format 'exit={{.State.ExitCode}}' life-init
```

### Step 5: Exit codes from the main process propagate.

```bash
docker run --rm alpine:3.24 sh -c 'exit 3'; echo "exit code: $?"
```

### Step 6: docker kill sends SIGKILL immediately.

```bash
docker start life
docker kill life
docker inspect --format 'exit={{.State.ExitCode}}' life
```

## Checks (expected output)

- After create: 'life Created'; after start: 'life Up ... seconds'
- inspect after pause prints 'paused'
- The first docker stop takes about 10 s (real ~0m10s) and the exit code is 137
- With --init the stop takes well under a second and exit is 143
- The sh -c 'exit 3' run prints 'exit code: 3'
- After docker kill the exit code is 137

## Stretch challenge

Run 'docker run -d --name life-t --stop-timeout 2 alpine:3.24 sleep 300' and time docker stop. Then explain which exit code you'd expect from a Python app with a SIGTERM handler that calls sys.exit(0).

## Cleanup

```bash
docker rm -f life life-init life-t 2>/dev/null
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Plain sleep as PID 1: docker stop took 10.15 s, exit 137. With --init: 0.16 s, exit 143.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
