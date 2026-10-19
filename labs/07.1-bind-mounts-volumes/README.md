# Lab 7.1: Bind-mounted page and a named volume

**Module M07 · Storage: writable layer, volumes, bind mounts and tmpfs** · about 25 min · [Lab index](../../README.md#lab-index)

**Goal:** Serve a host directory read-only through nginx, then persist data in a named volume across container replacement and back it up.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`pages/index.html`](pages/index.html) → copied to `~/labs/pages/index.html`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/pages && cp -a ~/shikumi-docker-labs/labs/07.1-bind-mounts-volumes/pages/. ~/labs/pages/
ls -A ~/labs/pages
```

### Step 1: Bind-mount a page read-only.

```bash
mkdir -p ~/labs/pages && cd ~/labs/pages
docker run -d --name pages -p 127.0.0.1:8081:80 -v "$PWD:/usr/share/nginx/html:ro" nginx:stable
sleep 1
curl -sS http://127.0.0.1:8081/
```

### Step 2: Edit on the host, request again: no rebuild needed. Then prove the container can't write.

```bash
printf '<h1>Version 2</h1>\n' > index.html
curl -sS http://127.0.0.1:8081/
docker exec pages sh -c 'echo hack > /usr/share/nginx/html/index.html' ; echo "write exit: $?"
```

### Step 3: Create a named volume and write to it from one container.

```bash
docker volume create --label course=shikumi notes-data
docker run --rm -v notes-data:/data alpine:3.24 sh -c 'date > /data/created.txt; echo note-1 >> /data/notes.txt'
docker volume inspect --format '{{.Mountpoint}} {{.Driver}}' notes-data
```

### Step 4: A different container sees the same data.

```bash
docker run --rm -v notes-data:/data alpine:3.24 cat /data/notes.txt
```

### Step 5: Back up the volume to a tarball, delete it, restore it.

```bash
cd ~/labs/m07 2>/dev/null || mkdir -p ~/labs/m07 && cd ~/labs/m07
docker run --rm -v notes-data:/data:ro -v "$PWD":/backup alpine:3.24 tar czf /backup/notes-data.tgz -C /data .
docker volume rm notes-data
docker volume create notes-data
docker run --rm -v notes-data:/data -v "$PWD":/backup:ro alpine:3.24 tar xzf /backup/notes-data.tgz -C /data
docker run --rm -v notes-data:/data alpine:3.24 cat /data/notes.txt
```

### Step 6: See pre-population: an empty named volume gets the image's files, a bind mount hides them.

```bash
docker run --rm -v html-vol:/usr/share/nginx/html nginx:stable ls /usr/share/nginx/html
mkdir -p empty && docker run --rm -v "$PWD/empty:/usr/share/nginx/html" nginx:stable ls /usr/share/nginx/html; echo '(bind mount: empty listing)'
```

### Step 7: tmpfs is memory-backed and size-limited.

```bash
docker run --rm --tmpfs /scratch:size=64m alpine:3.24 sh -c 'df -h /scratch; mount | grep scratch'
```

## Checks (expected output)

- First curl prints <h1>Version 1</h1>, second prints <h1>Version 2</h1>
- The write attempt fails with 'Read-only file system' and a non-zero 'write exit'
- volume inspect shows /var/lib/docker/volumes/notes-data/_data local
- The second container prints note-1
- After delete and restore, note-1 is printed again
- html-vol lists 50x.html and index.html; the empty bind mount lists nothing
- df shows a 64.0M tmpfs on /scratch

## Stretch challenge

Run 'docker run --rm -v "$PWD/owned:/out" alpine:3.24 touch /out/f' and check 'ls -ln owned'. Who owns the file and the directory, and how would --user "$(id -u):$(id -g)" change that?

## Cleanup

```bash
docker rm -f pages
docker volume rm html-vol
# keep notes-data: used in M14 cleanup lab
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). The read-only write failed with 'Read-only file system'. Backup/restore round-trip worked. Pre-population and tmpfs behaved as expected.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
