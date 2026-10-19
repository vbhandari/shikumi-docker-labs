# Lab 10.2: Profiles, overrides and watch

**Module M10 · Docker Compose** · about 30 min · [Lab index](../../README.md#lab-index)

**Goal:** Add a debug-only service via a profile, a dev override merged automatically, and live sync with compose watch.

## Before you start

- Lab 10.1 (the `shikumi` stack is running)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`app/.dockerignore`](app/.dockerignore) → copied to `~/labs/app/.dockerignore`
- [`app/Dockerfile`](app/Dockerfile) → copied to `~/labs/app/Dockerfile`
- [`app/app.py`](app/app.py) → copied to `~/labs/app/app.py`
- [`app/compose.override.yaml`](app/compose.override.yaml) → copied to `~/labs/app/compose.override.yaml`
- [`app/compose.yaml`](app/compose.yaml) → copied to `~/labs/app/compose.yaml`
- [`app/requirements.txt`](app/requirements.txt) → copied to `~/labs/app/requirements.txt`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/10.2-compose-profiles-watch/app/. ~/labs/app/
ls -A ~/labs/app
```

### Step 1: Add a .env file; the profile-gated debug service and the watch rules are in compose.override.yaml (copied in step 0).

```bash
cd ~/labs/app
cat compose.override.yaml
printf 'GREETING=hello from .env\n' > .env
docker compose config --services
docker compose --profile debug config --services
```

### Step 2: Apply the override and check the merged config.

```bash
docker compose up -d --wait
curl -sS http://127.0.0.1:8000/; echo
docker compose config | grep -A3 'environment:' | head -8
```

### Step 3: Start the debug profile service.

```bash
docker compose --profile debug up -d
sleep 3
docker compose --profile debug logs --tail 3 redis-ui
```

### Step 4: Terminal 2 (run alone, leave it running): open a second terminal on the VM and start watch. It stays in the foreground; do not paste anything after it.

<!-- verify: skip -->
```bash
# Terminal 2 - run alone; Ctrl-C here when step 5 is done
cd ~/labs/app && docker compose watch
```

### Step 5: Terminal 1: edit app.py, then check the watch output in terminal 2 and the API logs. Press Ctrl-C in terminal 2 when done.

<!-- verify: skip -->
```bash
# Terminal 1
cd ~/labs/app
sed -i 's/hello from shikumi/hello from watch/' app.py
sleep 10
docker compose logs --tail 5 api
curl -sS http://127.0.0.1:8000/; echo
```

## Checks (expected output)

- config --services lists api and redis; with --profile debug it adds redis-ui
- The response shows message 'dev override active' and greeting 'hello from .env'
- redis-ui logs show '# Keyspace' and 'db0:keys=1,...'
- After the edit (with the override's MESSAGE removed or overridden) watch logs show files being synced and the service restarting

## Stretch challenge

Remove MESSAGE from the override so the edit to the default message is visible, add an 'ignore' list to the watch rule (for example __pycache__/), and explain when 'rebuild' is needed instead of 'sync'.

## Instructor check (optional, not for learners)

Instructor-only check (not for learners): non-interactive variant of steps 4-5, used for unattended verification. Run it before the cleanup.

<!-- verify: instructor -->
```bash
(timeout 40 docker compose watch > /tmp/watch.log 2>&1 &)
sleep 12
sed -i 's/hello from shikumi/hello from watch/' app.py
sleep 15
curl -sS http://127.0.0.1:8000/; echo
grep -iE 'sync|restart' /tmp/watch.log | head -5
```

## Cleanup

```bash
docker compose --profile debug down
rm -f compose.override.yaml .env
sed -i 's/hello from watch/hello from shikumi/' app.py
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). The interactive 'docker compose watch' step was run in its scripted variant. The watch log showed 'Syncing service "api" after 1 changes were detected' and 'service(s) ["api"] restarted'.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
