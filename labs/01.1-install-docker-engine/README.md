# Lab 1.1: Install Docker Engine and verify it

**Module M01 · Install and configure Docker Engine on Ubuntu / Debian** · about 30 min · [Lab index](../../README.md#lab-index)

**Goal:** Install Docker Engine from the official apt repository on your VM and prove client, daemon and plugins work.

## Before you start

- A fresh Ubuntu 24.04/26.04 LTS or Debian 12/13 (64-bit) VM with a sudo user
- This repo cloned to ~/shikumi-docker-labs (needs `git`: `sudo apt-get install -y git`)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`scripts/install-docker-debian.sh`](scripts/install-docker-debian.sh)
- [`scripts/install-docker-ubuntu.sh`](scripts/install-docker-ubuntu.sh)

## Steps

### Step 1: Remove conflicting packages (Ubuntu list shown; on Debian drop docker-compose-v2).

<!-- verify: skip -->
```bash
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc | cut -f1)
```

### Step 2: Add Docker's GPG key and apt repository (Ubuntu shown). On Debian use the linux/debian URLs and $VERSION_CODENAME, or run scripts/install-docker-debian.sh from this folder, which does steps 2-3 for you (scripts/install-docker-ubuntu.sh is the Ubuntu equivalent).

<!-- verify: skip -->
```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
```

### Step 3: Install the five packages (skip if you ran one of the install scripts).

<!-- verify: skip -->
```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Step 4: Confirm the service is running and run the test image with sudo.

<!-- verify: skip -->
```bash
sudo systemctl status docker --no-pager
sudo docker run hello-world
```

### Step 5: Add yourself to the docker group. The new group only applies to new logins: log out and back in (or SSH in again), or run 'newgrp docker' to start a shell that already has it.

<!-- verify: skip -->
```bash
getent group docker
sudo usermod -aG docker $USER
# Log out and back in (or: newgrp docker), then continue
newgrp docker
```

### Step 6: After logging back in (or in the newgrp shell), check versions, plugins and the current context.

```bash
id -nG
docker version
docker info --format '{{.ServerVersion}} {{.Driver}} {{.CgroupVersion}}'
docker compose version
docker buildx version
docker context ls
```

## Checks (expected output)

- apt update lists download.docker.com without signature errors
- systemctl status shows 'active (running)'
- hello-world prints 'Hello from Docker!' and exits
- id -nG includes docker after re-login
- docker version shows both a Client and a Server section (29.x at time of writing)
- docker info on a fresh 29.x install reports storage driver 'overlayfs' (containerd image store) and cgroup version 2
- docker context ls shows 'default *' pointing at unix:///var/run/docker.sock

## Stretch challenge

Configure log rotation in /etc/docker/daemon.json (max-size 10m, max-file 3), validate it with 'sudo dockerd --validate --config-file /etc/docker/daemon.json', restart Docker and create a container: confirm with docker inspect --format '{{.HostConfig.LogConfig}}' NAME.

## Cleanup

```bash
docker ps -aq --filter ancestor=hello-world | xargs -r docker rm
```

## Tested

Partially verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). Step 6 was run on the build machine. Steps 2-3 (apt repository + package install) were run verbatim in clean ubuntu:24.04, ubuntu:26.04, debian:12 and debian:13 containers: all installed Docker 29.9.1, Compose v5.6.0, Buildx v0.38.0 and auto-created the docker group. Steps 1, 4 and 5 (apt remove, systemctl, usermod + re-login) need a real VM with systemd and were not run.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
