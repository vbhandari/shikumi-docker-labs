# Lab 6.1: Run a local registry and push by tag and digest

**Module M06 · Registries, tagging and distribution** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** Push the course image to a local registry, query the registry API, and pull by digest.

## Before you start

- Lab 5.2 (image `myapi:2.0`)
- Run the steps in order, in the same terminal, unless a step says otherwise.

If you skipped the earlier lab, run this first:

```bash
docker image inspect myapi:2.0 >/dev/null 2>&1 || { mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/05.2-multi-stage-build/app/. ~/labs/app/ && docker build -t myapi:2.0 ~/labs/app; }
```

## Steps

### Step 1: Start a registry bound to loopback (host port 5001; 5000 is the API).

```bash
docker run -d --name registry --restart unless-stopped -p 127.0.0.1:5001:5000 -v registry-data:/var/lib/registry registry:3
sleep 2
curl -sS http://127.0.0.1:5001/v2/
```

### Step 2: Tag the API with a version, a git-style SHA and a moving minor tag; push.

```bash
docker tag myapi:2.0 localhost:5001/shikumi-api:2.0.0
docker tag myapi:2.0 localhost:5001/shikumi-api:2.0
docker tag myapi:2.0 localhost:5001/shikumi-api:sha-0000001
docker push --all-tags localhost:5001/shikumi-api
```

### Step 3: Ask the registry what it has.

```bash
curl -sS http://127.0.0.1:5001/v2/_catalog
curl -sS http://127.0.0.1:5001/v2/shikumi-api/tags/list
```

### Step 4: Inspect the remote manifest without pulling, and capture its digest.

```bash
docker buildx imagetools inspect localhost:5001/shikumi-api:2.0.0
DIGEST=$(docker buildx imagetools inspect localhost:5001/shikumi-api:2.0.0 --format '{{json .Manifest.Digest}}' | tr -d '"')
echo $DIGEST
```

### Step 5: Remove the local tags and pull by digest.

```bash
docker image rm localhost:5001/shikumi-api:2.0.0 localhost:5001/shikumi-api:2.0 localhost:5001/shikumi-api:sha-0000001
docker pull localhost:5001/shikumi-api@$DIGEST
docker run --rm --entrypoint python localhost:5001/shikumi-api@$DIGEST -c 'print("ran by digest")'
```

## Checks (expected output)

- curl /v2/ returns '{}' (HTTP 200)
- docker push prints a digest line for each tag; all three tags share one digest
- _catalog returns {"repositories":["shikumi-api"]} and tags/list lists 2.0, 2.0.0, sha-0000001
- imagetools inspect prints Name, MediaType and Digest: sha256:...
- Pull by digest succeeds; the container prints 'ran by digest'

## Stretch challenge

Move the '2.0' tag to a new build (change the message, rebuild, tag and push 2.0 only). Show that pulling by the old digest still gives the old image while '2.0' gives the new one.

## Cleanup

```bash
# keep the registry running: M15 and M16 use it
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). registry:3 (3.1.x). All tags shared one index digest, which includes a provenance attestation manifest; the container ran by digest.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
