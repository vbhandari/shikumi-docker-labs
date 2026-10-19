# Lab 5.3: A multi-platform image and a Buildx builder

**Module M05 · Build cache, multi-stage builds and BuildKit / Buildx** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** Build a two-platform image without emulation, inspect the index, and try a container builder.

## Before you start

- Lab 1.1 (containerd image store, the default on a fresh Docker 29 install)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`multi/Dockerfile`](multi/Dockerfile) → copied to `~/labs/multi/Dockerfile`
- [`multi/index.html`](multi/index.html) → copied to `~/labs/multi/index.html`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/multi && cp -a ~/shikumi-docker-labs/labs/05.3-multi-platform-buildx/multi/. ~/labs/multi/
ls -A ~/labs/multi
```

### Step 1: Go to the static-site project you copied: a tiny image that needs no RUN on the target platform.

```bash
mkdir -p ~/labs/multi && cd ~/labs/multi
cat Dockerfile
```

### Step 2: Build for two platforms into the local image store.

```bash
docker build --platform linux/amd64,linux/arm64 -t shikumi/site:multi .
docker image ls --tree shikumi/site:multi
```

### Step 3: Run the native variant.

```bash
docker run -d --name site -p 127.0.0.1:8080:80 shikumi/site:multi
sleep 1
curl -sS http://127.0.0.1:8080/
```

### Step 4: Create a docker-container builder, build with it, then remove it.

```bash
docker buildx create --name shikumi --driver docker-container --bootstrap
docker buildx ls
docker buildx build --builder shikumi -t shikumi/site:bk --load .
docker buildx rm shikumi
```

## Checks (expected output)

- docker image ls --tree lists linux/amd64 and linux/arm64 under shikumi/site:multi
- curl returns '<h1>shikumi multi-platform</h1>'
- buildx ls shows the shikumi builder with driver docker-container and status running
- The --load build ends with an import to the docker image store and shikumi/site:bk appears in docker image ls

## Stretch challenge

Write a docker-bake.hcl with a target 'site' (context '.', tags ['shikumi/site:bake'], platforms ['linux/amd64','linux/arm64']) and run 'docker buildx bake --print site', then 'docker buildx bake site'.

## Cleanup

```bash
docker rm -f site
docker image rm shikumi/site:bk
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Two-platform build into the containerd image store worked without QEMU. The docker-container builder ran BuildKit v0.33.1.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
