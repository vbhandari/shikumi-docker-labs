# Lab 2.1: An image and a stopped container

**Module M02 · The container lifecycle** · about 10 min · [Lab index](../../README.md#lab-index)

**Goal:** See that a container that finishes is 'Exited', still exists, and can be inspected and removed while the image stays cached.

## Before you start

- Lab 1.1 (Docker installed, your user in the docker group)
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Steps

### Step 1: Run hello-world with a name.

```bash
docker run --name lab-hello hello-world
```

### Step 2: Compare images, running containers and all containers.

```bash
docker image ls
docker ps
docker ps -a --filter name=lab-hello
```

### Step 3: Read its output again and its exit code.

```bash
docker logs lab-hello
docker inspect --format '{{.State.Status}} exit={{.State.ExitCode}}' lab-hello
```

### Step 4: Remove the container; the image stays.

```bash
docker rm lab-hello
docker image ls hello-world
```

## Checks (expected output)

- hello-world prints 'Hello from Docker!' and exits
- docker ps shows nothing for lab-hello; docker ps -a shows it as 'Exited (0)'
- inspect prints 'exited exit=0'
- After rm, hello-world:latest is still listed by docker image ls

## Stretch challenge

Run 'docker run --rm hello-world' and show that nothing is left in docker ps -a. Explain when --rm is the right default.

## Cleanup

Nothing to clean up.

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). All steps ran on the build machine; outputs match the expected checks.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
