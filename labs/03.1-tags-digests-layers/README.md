# Lab 3.1: Tags, digests, layers and platforms

**Module M03 · Images, layers and the image store** · about 25 min · [Lab index](../../README.md#lab-index)

**Goal:** Pull an image by tag and by digest, read its layers, history and platforms, and move it with save/load.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: Pull by tag and show the digest.

```bash
docker pull nginx:stable
docker image ls --digests nginx
```

### Step 2: Show the platforms behind the tag and which one is unpacked locally.

```bash
docker buildx imagetools inspect nginx:stable | head -20
docker image ls --tree nginx:stable
```

### Step 3: Read config and layers.

```bash
docker image inspect --format 'os={{.Os}} arch={{.Architecture}} layers={{len .RootFS.Layers}}' nginx:stable
docker image inspect --format '{{json .Config.Cmd}} {{json .Config.ExposedPorts}}' nginx:stable
docker history nginx:stable
```

### Step 4: Pull by digest: copy the digest from 'docker image ls --digests' into DIGEST.

```bash
DIGEST=$(docker image inspect --format '{{index .RepoDigests 0}}' nginx:stable)
echo "$DIGEST"
docker pull "$DIGEST"
```

### Step 5: Add your own tag, then remove only the tag.

```bash
docker tag nginx:stable shikumi/nginx:training
docker image ls shikumi/nginx
docker image rm shikumi/nginx:training
docker image ls nginx
```

### Step 6: Export to a tar and load it back (offline transfer).

```bash
mkdir -p ~/labs/m03 && cd ~/labs/m03
docker pull -q busybox:1.37
docker save -o busybox.tar busybox:1.37
ls -lh busybox.tar
docker image rm busybox:1.37
docker load -i busybox.tar
docker image ls busybox
```

## Checks (expected output)

- --digests shows a sha256:... value next to nginx:stable
- imagetools inspect shows 'MediaType: application/vnd.oci.image.index.v1+json' and several Platform entries (linux/amd64, linux/arm64/v8, ...)
- --tree marks only your VM's platform with non-zero disk usage
- inspect prints os=linux arch=amd64 (or arm64) and a layer count (7 for nginx:stable 1.30.6 on 19 Oct 2026); Cmd is ["nginx","-g","daemon off;"] and port 80/tcp is exposed
- docker history shows many 0B metadata rows (ENV, EXPOSE, CMD) - row count is not layer count
- Pulling by digest reports the image is up to date (same content)
- Removing shikumi/nginx:training prints 'Untagged:' and nginx:stable stays
- Pulling by digest also adds an untagged 'nginx@sha256:...' row to docker image ls
- busybox.tar is a few MB; docker load prints 'Loaded image: busybox:1.37'

## Stretch challenge

Pull 'alpine:3.24' with --platform linux/arm64 and look at docker image ls --tree alpine:3.24 again. What changed, and why can't you run it on an amd64 VM without emulation?

## Cleanup

```bash
rm -f ~/labs/m03/busybox.tar
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). nginx:stable was 1.30.6 on trixie-slim with 7 layers on 19 Oct 2026. The digest will differ when the tag moves.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
