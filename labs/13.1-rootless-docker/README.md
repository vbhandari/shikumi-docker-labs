# Lab 13.1: Rootless Docker for a second user (VM only)

**Module M13 · Security** · about 25 min · [Lab index](../../README.md#lab-index)

**Goal:** Set up rootless Docker for a dedicated user on your VM and show that container processes run under that user's subordinate IDs.

## Before you start

- A VM snapshot (this lab adds a user and a second Docker daemon)
- A second terminal / SSH session on the VM
- systemd as PID 1 (any normal Ubuntu/Debian VM; not a container)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: Terminal 1, your own user: install prerequisites and create a user.

<!-- verify: skip -->
```bash
# Terminal 1 - your own user
sudo apt install -y uidmap docker-ce-rootless-extras dbus-user-session systemd-container
sudo useradd -m -s /bin/bash rl
grep ^rl: /etc/subuid /etc/subgid
```

### Step 2: Terminal 2 (your normal user): open a second terminal and start a full login session as rl there (machinectl gives it a systemd user session). Keep terminal 1 as your own shell.

<!-- verify: skip -->
```bash
# Terminal 2 - your normal user
sudo machinectl shell rl@
```

### Step 3: Terminal 2, AS USER rl: install rootless Docker. --force is needed because the rootful daemon keeps running for the rest of the course.

<!-- verify: skip -->
```bash
# Terminal 2 - AS USER rl (prompt shows rl@...)
dockerd-rootless-setuptool.sh install --force
docker context ls
docker info --format '{{.SecurityOptions}}'
```

### Step 4: Terminal 2, AS USER rl: run a container on the rootless daemon and reach it.

<!-- verify: skip -->
```bash
# Terminal 2 - AS USER rl
docker run -d --name rl-web -p 127.0.0.1:8082:80 nginx:stable
curl -sI http://127.0.0.1:8082 | head -1
```

### Step 5: Terminal 1, YOUR OWN USER (not rl): look at who owns the nginx processes.

<!-- verify: skip -->
```bash
# Terminal 1 - your own user
ps -o user:12,pid,cmd -C nginx
```

## Checks (expected output)

- /etc/subuid and /etc/subgid each contain a line 'rl:<start>:65536'
- The setup tool prints 'Installed docker.service successfully' and 'Current context is now "rootless"'
- docker info SecurityOptions include name=rootless
- curl prints HTTP/1.1 200 OK
- ps shows the nginx master owned by rl and workers owned by a high numeric UID from rl's subuid range

## Stretch challenge

As rl, try 'docker run -p 127.0.0.1:80:80 nginx:stable'. Read the error, then find the documented fix in the rootless tips page and explain its security trade-off.

## Cleanup

<!-- verify: skip -->
```bash
# Terminal 2 - AS USER rl: remove the container, the rootless daemon and its data, then leave the rl session
docker rm -f rl-web
dockerd-rootless-setuptool.sh uninstall
rootlesskit rm -rf ~/.local/share/docker
exit
# Terminal 1 - your own user: stop rl's remaining processes, then delete the user
sudo loginctl terminate-user rl
sudo userdel -r rl
```

## Tested

Not verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). The build machine has no systemd as PID 1, which rootless setup needs (systemd --user service). Steps follow docs.docker.com/engine/security/rootless as of Oct 2026. Test on a VM snapshot before class.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
