# Lab 13.2: Capabilities, no-new-privileges and a read-only root

**Module M13 · Security** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** See capabilities in action, run the API hardened, and prove what the restrictions block.

## Before you start

- Lab 5.2 (image `myapi:2.0`)
- Run the steps in order, in the same terminal, unless a step says otherwise.

If you skipped the earlier lab, run this first:

```bash
docker image inspect myapi:2.0 >/dev/null 2>&1 || { mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/05.2-multi-stage-build/app/. ~/labs/app/ && docker build -t myapi:2.0 ~/labs/app; }
```

## Steps

### Step 1: Default containers have a reduced capability set; dropping all blocks chown.

```bash
docker run --rm alpine:3.24 sh -c 'grep CapEff /proc/1/status; chown nobody /tmp && echo chown-ok'
docker run --rm --cap-drop ALL alpine:3.24 sh -c 'chown nobody /tmp && echo chown-ok'
docker run --rm --cap-drop ALL --cap-add CHOWN alpine:3.24 sh -c 'chown nobody /tmp && echo chown-ok'
```

### Step 2: Run the API hardened.

```bash
docker run -d --name api-hard --read-only --tmpfs /tmp:size=16m --cap-drop ALL --security-opt no-new-privileges:true --user 10001:10001 -p 127.0.0.1:5002:5000 myapi:2.0
sleep 3
curl -sS http://127.0.0.1:5002/; echo
```

### Step 3: Prove the restrictions.

```bash
docker exec api-hard id
docker exec api-hard sh -c 'touch /app/x' ; echo "write to /app exit: $?"
docker exec api-hard sh -c 'touch /tmp/ok && echo tmp-writable'
docker exec api-hard grep -E 'CapEff|NoNewPrivs' /proc/1/status
docker inspect --format 'ro={{.HostConfig.ReadonlyRootfs}} caps={{.HostConfig.CapDrop}} sec={{.HostConfig.SecurityOpt}}' api-hard
```

## Checks (expected output)

- Default CapEff is a non-zero mask (e.g. 00000000a80425fb) and chown-ok prints
- With --cap-drop ALL chown fails: 'Operation not permitted'
- Adding back CHOWN prints chown-ok again
- The hardened API answers on port 5002 (gunicorn needs no extra capabilities on port 5000)
- id prints uid=10001; writing /app fails with 'Read-only file system'; /tmp is writable
- CapEff 0000000000000000 and NoNewPrivs 1; inspect shows ro=true caps=[ALL] sec=[no-new-privileges:true]

## Stretch challenge

Try running nginx:stable with --cap-drop ALL. It fails - read the logs and add back the minimum capabilities it needs (hint: it chowns and setuids to its worker user, and binds port 80). Compare with nginxinc/nginx-unprivileged.

## Cleanup

```bash
docker rm -f api-hard
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Default CapEff 00000000a80425fb. cap-drop ALL blocked chown and --cap-add CHOWN restored it. Hardened API ran with CapEff 0 and NoNewPrivs 1.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
