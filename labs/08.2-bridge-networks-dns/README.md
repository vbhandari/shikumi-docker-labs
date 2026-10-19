# Lab 8.2: Names on a bridge, isolation and special networks

**Module M08 · Networking** · about 25 min · [Lab index](../../README.md#lab-index)

**Goal:** Show DNS on user-defined bridges, its absence on the default bridge, network isolation, aliases, internal networks and host/none.

## Before you start

- Lab 1.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: Default bridge: names don't resolve.

```bash
docker run -d --name a1 nginx:stable
docker run --rm alpine:3.24 wget -qO- -T 3 http://a1 ; echo "exit: $?"
```

### Step 2: User-defined bridge: names resolve.

```bash
docker network create --label course=shikumi labnet
docker run -d --name site --network labnet nginx:stable
sleep 1
docker run --rm --network labnet alpine:3.24 wget -qO- http://site:80 | grep -o '<title>.*</title>'
```

### Step 3: Aliases and multi-network membership.

```bash
docker network create --label course=shikumi backend
docker network connect --alias web-alias backend site
docker run --rm --network backend alpine:3.24 wget -qO- http://web-alias | grep -o '<title>.*</title>'
docker inspect --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' site
```

### Step 4: Isolation: a container only on labnet can't reach one only on backend.

```bash
docker run -d --name hidden --network backend nginx:stable
docker run --rm --network labnet alpine:3.24 wget -qO- -T 3 http://hidden ; echo "exit: $?"
```

### Step 5: Internal network: no route to the outside world.

```bash
docker network create --internal --label course=shikumi sealed
docker run --rm --network sealed alpine:3.24 wget -qO- -T 3 http://example.com ; echo "exit: $?"
```

### Step 6: none and host networks.

```bash
docker run --rm --network none alpine:3.24 ip -o link
docker run --rm --network host alpine:3.24 ip -o link | head -4
```

## Checks (expected output)

- On the default bridge wget fails (exit 1): 'bad address' or 'download timed out', depending on the VM's upstream DNS
- On labnet the client prints '<title>Welcome to nginx!</title>'
- From the backend network the alias web-alias reaches site ('<title>Welcome to nginx!</title>'); site is attached to 'backend labnet'
- Reaching 'hidden' from labnet fails (exit 1): the name is unknown on labnet, so wget reports 'bad address' or a DNS timeout
- On the internal network wget fails with 'bad address' for example.com (no external DNS or route), exit 1
- --network none lists only 'lo'; --network host lists the VM's real interfaces (eth0/ens*, docker0, br-*)

## Stretch challenge

Replace 'site' with redis:8.8-alpine named 'cache' on labnet and run 'docker run --rm --network labnet redis:8.8-alpine redis-cli -h cache ping'. Why does this need no -p at all?

## Cleanup

```bash
docker rm -f a1 site hidden
docker network rm labnet backend sealed
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). On the default bridge, name lookup ended in a DNS timeout, not 'bad address'.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
