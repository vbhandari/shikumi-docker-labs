# Lab 14.1: Measure, then prune selectively

**Module M14 · Cleanup and pruning** · about 15 min · [Lab index](../../README.md#lab-index)

**Goal:** Measure disk usage, create labelled clutter, and remove exactly that clutter while protecting data volumes.

## Before you start

- Lab 7.1 (volume `notes-data`) and Lab 13.4 (volume `trivy-cache`)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: Measure first.

```bash
docker system df
docker system df -v | head -30
```

### Step 2: Create labelled clutter: stopped containers, an anonymous volume, a network.

```bash
for i in 1 2 3; do docker run --label course=shikumi --name junk$i alpine:3.24 true; done
docker run --label course=shikumi -v /data --name junk-anon alpine:3.24 true
docker network create --label course=shikumi junknet
docker ps -a --filter label=course=shikumi --format '{{.Names}} {{.Status}}'
```

### Step 3: Remove only labelled stopped containers, then only labelled networks.

```bash
docker container prune -f --filter label=course=shikumi
docker network prune -f --filter label=course=shikumi
```

### Step 4: Volumes: default prune removes anonymous volumes only; named notes-data survives.

```bash
docker volume ls --filter label=course=shikumi
docker volume prune -f
docker volume ls --filter name=notes-data
```

### Step 5: Images: dangling vs unused, and build cache older than a day.

```bash
docker image prune -f
docker image ls --filter dangling=true
docker builder prune -f --filter until=24h
docker system df
```

## Checks (expected output)

- system df lists Images, Containers, Local Volumes and Build Cache with RECLAIMABLE
- Four junk containers show 'Exited (0)'
- container prune reports the junk container IDs and 'Total reclaimed space'; network prune deletes junknet
- volume prune removes the anonymous volume from junk-anon; notes-data is still listed
- No dangling images remain; build cache shrinks or reports 0B reclaimed

## Stretch challenge

Write ~/bin/docker-tidy.sh that prunes containers and networks labelled course=shikumi older than 2h (--filter until=2h) and prints docker system df before and after. Why is 'until' not supported for volume prune?

## Cleanup

```bash
docker volume rm notes-data trivy-cache 2>/dev/null || true
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Label-filtered container/network prune removed only course resources. Default volume prune removed only the anonymous volume.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
