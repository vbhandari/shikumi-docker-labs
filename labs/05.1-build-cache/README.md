# Lab 5.1: Rebuild after a source edit

**Module M05 · Build cache, multi-stage builds and BuildKit / Buildx** · about 15 min · [Lab index](../../README.md#lab-index)

**Goal:** Show that a source-only edit reuses the dependency layer, and that a new image does not change a running container.

## Before you start

- Lab 4.1 (image `myapi:v1`)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`app/.dockerignore`](app/.dockerignore) → copied to `~/labs/app/.dockerignore`
- [`app/Dockerfile`](app/Dockerfile) → copied to `~/labs/app/Dockerfile`
- [`app/app.py`](app/app.py) → copied to `~/labs/app/app.py`
- [`app/requirements.txt`](app/requirements.txt) → copied to `~/labs/app/requirements.txt`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/05.1-build-cache/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Start v1 again, then change the message to v2.

```bash
cd ~/labs/app
docker run -d --name api -p 127.0.0.1:5000:5000 myapi:v1
sed -i 's/hello v1/hello v2/' app.py
grep -n 'hello v' app.py
```

### Step 2: Predict which steps will be CACHED, then build with plain progress.

```bash
docker build --progress=plain -t myapi:v2 . 2>&1 | grep -E '^#[0-9]+ \[|CACHED'
```

### Step 3: The running container still serves v1: images don't update containers.

```bash
curl -sS http://127.0.0.1:5000/
```

### Step 4: Replace the container and verify.

```bash
docker rm -f api
docker run -d --name api -p 127.0.0.1:5000:5000 myapi:v2
sleep 2
curl -sS http://127.0.0.1:5000/
```

### Step 5: Now change a dependency and watch the cascade.

```bash
printf 'Flask==3.1.3\nblinker>=1.9\n' > requirements.txt
docker build --progress=plain -t myapi:v2b . 2>&1 | grep -E 'CACHED|pip install'
```

## Checks (expected output)

- grep shows message="hello v2" in app.py
- Build output marks the requirements COPY and 'RUN pip install' steps CACHED; only 'COPY app.py' runs
- The old container still returns hello v1 (and greeting none - no -e this time)
- After replacement curl returns hello v2
- After editing requirements.txt the pip install step is no longer CACHED

## Stretch challenge

Use 'docker build --no-cache' once and compare the build time. Then explain why a scheduled CI rebuild should use --pull as well.

## Cleanup

```bash
docker rm -f api
cd ~/labs/app && printf 'Flask==3.1.3\n' > requirements.txt
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). COPY requirements.txt and RUN pip install were CACHED after a source-only edit. pip install re-ran after the requirements.txt content changed.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
