# Lab 8.1: Publish a port and verify it

**Module M08 · Networking** · about 20 min · [Lab index](../../README.md#lab-index)

**Goal:** Prove that a running container is unreachable on host localhost until a port is published, then publish on loopback.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: If nginx is installed on the VM, stop it so it can't answer (skip if not installed).

<!-- verify: skip -->
```bash
sudo systemctl stop nginx
```

### Step 2: Run nginx without publishing and try to reach it.

```bash
docker run -d --name web nginx:stable
docker ps --filter name=web --format '{{.Names}} {{.Ports}}'
curl --max-time 2 http://127.0.0.1:80 ; echo "curl exit: $?"
docker port web
```

### Step 3: The container is reachable by its bridge IP from the VM (but never hard-code IPs).

```bash
IP=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web)
echo $IP
curl -sS -o /dev/null -w '%{http_code}\n' http://$IP:80
```

### Step 4: Recreate with a loopback-only published port.

```bash
docker rm -f web
docker run -d --name web -p 127.0.0.1:8080:80 nginx:stable
docker port web
sleep 1
curl -sI http://127.0.0.1:8080 | head -1
```

### Step 5: Peek inside with exec: logs, processes, PID 1.

```bash
docker logs --tail 3 web
docker top web
docker exec web cat /proc/1/comm
docker exec web sh -c 'for t in ps curl bash; do command -v $t || echo "$t: not found"; done'
```

## Checks (expected output)

- docker ps shows '80/tcp' with no host mapping
- The first curl fails (curl exit 7 'Couldn't connect') and docker port prints nothing
- curl to the bridge IP returns 200
- docker port prints '80/tcp -> 127.0.0.1:8080'; curl -I prints 'HTTP/1.1 200 OK'
- docker top lists an nginx master and worker processes; /proc/1/comm is nginx
- The tool loop prints 'ps: not found' (and curl, depending on the image build) - minimal images omit tools; use docker top instead of ps

## Stretch challenge

Publish with '-p 8080:80' (no IP) and run 'ss -ltn | grep 8080'. Which addresses is it listening on, and what would a ufw 'deny 8080' rule do?

## Cleanup

```bash
docker rm -f web
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Step 1 (systemctl stop nginx) was not run because the build machine has no host nginx and no systemd. nginx:stable has bash and curl but no ps.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
