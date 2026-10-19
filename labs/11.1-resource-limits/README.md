# Lab 11.1: Configured limits, real throttling and an OOM kill

**Module M11 · Resource limits and runtime controls** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** Show configured limits, CPU throttling under load, an OOM kill, a PID limit and a live update.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: Configured limits on an idle container.

```bash
docker run -d --name limited --memory=128m --cpus=0.5 alpine:3.24 sleep 300
docker stats --no-stream limited
docker inspect limited --format '{{.HostConfig.Memory}} {{.HostConfig.NanoCpus}}'
```

### Step 2: Now generate real CPU load and watch it stay near 50%.

```bash
docker run -d --name burner --cpus=0.5 alpine:3.24 sh -c 'while :; do :; done'
sleep 5
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' burner
```

### Step 3: Raise the quota live with docker update.

```bash
docker update --cpus=1 burner
sleep 5
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' burner
```

### Step 4: Exceed a memory limit: the kernel kills the process.

```bash
docker run --name oom --memory=64m --memory-swap=64m alpine:3.24 sh -c 'tail /dev/zero' ; echo "exit: $?"
docker inspect --format 'OOMKilled={{.State.OOMKilled}} exit={{.State.ExitCode}}' oom
```

### Step 5: A PID limit stops runaway process creation.

```bash
docker run --rm --pids-limit=20 alpine:3.24 sh -c 'for i in $(seq 1 40); do sleep 30 & done; wait' 2>&1 | head -3
```

## Checks (expected output)

- stats shows LIMIT 128MiB; inspect prints 134217728 500000000
- burner CPU % hovers around 50%
- After docker update --cpus=1 it rises to around 100%
- The oom run exits with 137; inspect prints OOMKilled=true exit=137
- The PID-limited run prints 'can't fork: Resource temporarily unavailable' errors

## Stretch challenge

Run the API with --memory=64m and use 'docker stats' while you send 200 requests with a loop. Then add --memory-reservation=32m and explain the difference between a reservation and a limit.

## Cleanup

```bash
docker rm -f limited burner oom
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). CPU 49.75% at --cpus=0.5, then 99.28% after docker update --cpus=1. OOMKilled=true exit=137. pids-limit produced 'can't fork'.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
