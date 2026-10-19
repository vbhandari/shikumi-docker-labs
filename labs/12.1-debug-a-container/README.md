# Lab 12.1: Investigate a misbehaving container

**Module M12 · Logging, debugging and observability** · about 30 min · [Lab index](../../README.md#lab-index)

**Goal:** Use logs, inspect, events, stats, diff and cp to explain what a container did, then debug a tool-less image through shared namespaces.

## Before you start

- Lab 10.1 (step 6 starts the stack if it isn't running)
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
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/12.1-debug-a-container/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Install jq (used in step 6; minimal Debian/Ubuntu images don't ship it).

<!-- verify: skip -->
```bash
sudo apt-get install -y jq
```

### Step 2: Start a container with the local log driver and noisy output (work in ~/labs/m12).

```bash
mkdir -p ~/labs/m12 && cd ~/labs/m12
docker run -d --name noisy --log-driver local --log-opt max-size=1m alpine:3.24 sh -c 'i=0; while :; do i=$((i+1)); echo "tick $i"; [ $((i % 5)) -eq 0 ] && echo "warn $i" >&2; sleep 1; done'
sleep 6
docker logs --tail 3 -t noisy
docker logs noisy 2>&1 >/dev/null | tail -2
docker inspect --format '{{.HostConfig.LogConfig.Type}} {{json .HostConfig.LogConfig.Config}}' noisy
```

### Step 3: What changed in its filesystem? Copy a file out.

```bash
docker exec noisy sh -c 'echo debug > /tmp/marker'
docker diff noisy
docker cp noisy:/tmp/marker ./marker.txt && cat marker.txt
```

### Step 4: Live usage and process list.

```bash
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}' noisy
docker top noisy
```

### Step 5: Watch the event stream while you restart it. Interactively: run 'docker events --filter container=noisy' in a second terminal. (-t 2 because sh as PID 1 ignores SIGTERM, see M02.)

```bash
(timeout 10 docker events --filter container=noisy --format '{{.Time}} {{.Action}}' > events.txt &)
sleep 1
docker restart -t 2 noisy >/dev/null
sleep 4
cat events.txt
```

### Step 6: Health status of the M10 API (start the stack if it isn't running).

```bash
cd ~/labs/app && docker compose up -d --wait
docker inspect --format '{{json .State.Health}}' shikumi-api-1 | jq '{Status, FailingStreak, last: .Log[-1].ExitCode}'
```

### Step 7: Debug a container without tools: join its PID and network namespaces with busybox.

```bash
docker run --rm --pid container:shikumi-api-1 busybox:1.37 ps
docker run --rm --network container:shikumi-api-1 busybox:1.37 wget -qO- http://127.0.0.1:5000/healthz; echo
```

## Checks (expected output)

- docker logs -t shows RFC3339 timestamps and 'tick N'; stderr-only lines show 'warn N'
- LogConfig shows local {"max-size":"1m"}
- docker diff shows 'C /tmp' and 'A /tmp/marker'; marker.txt contains debug
- stats shows a few hundred KiB of memory and 2-3 PIDs
- events.txt lists kill, kill (SIGKILL after the 2 s timeout), stop, die, start, restart
- Health JSON shows Status 'healthy' and last exit code 0
- busybox ps lists gunicorn processes (PID 1 is gunicorn); wget prints {"status":"ok"}

## Stretch challenge

Break the API on purpose: 'docker compose stop redis' and call http://127.0.0.1:8000/. Use logs, inspect and events to write a three-line incident note: symptom, evidence, cause.

## Cleanup

```bash
docker rm -f noisy
rm -f ~/labs/m12/marker.txt ~/labs/m12/events.txt
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). docker events history (--since/--until) lost recent entries on the busy build machine, so the lab streams events during the restart instead. busybox namespace-join debugging worked on the tool-less API.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
