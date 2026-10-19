# Shikumi Labs · Docker CLI: From First Container to Production: hands-on labs

*Hands-on Docker for software engineers, beginner to expert.*

This repository holds the lab files and step-by-step instructions for the Shikumi Labs Docker course: 17 modules and 24 hands-on labs, from installing Docker Engine to deploying a hardened Compose stack from a private registry, and a final audit that prepares you for Kubernetes. The slides teach the concepts; every lab here is something you run yourself on your own VM.

## What you need (VM prerequisites)

- **One VM per learner:** Ubuntu 24.04 LTS / 26.04 LTS or Debian 12 / 13 (64-bit).
- **Resources:** 2 vCPU, 4 GB RAM, 20 GB free disk, outbound HTTPS to Docker Hub and PyPI, sudo user, SSH access.
- **systemd as PID 1** (any normal VM; Lab 13.1 rootless Docker needs it). Not WSL1, not a container.
- **Packages:** `git` and `curl` (`sudo apt-get install -y git curl`). Lab 1.1 installs Docker; Labs 12.1 and 16.1 install `jq`.
- **Free ports on 127.0.0.1:** 5000, 5001, 5002, 8000, 8080, 8081, 8082, 8090.
- **No Kubernetes cluster.** Module M16 prepares you for a later Kubernetes course without installing one.
- Tested with Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0 (October 2026).

## Get the labs

```bash
sudo apt-get update && sudo apt-get install -y git curl
cd ~
git clone https://github.com/vbhandari/shikumi-docker-labs.git
cd ~/shikumi-docker-labs && ls labs
```

The labs assume the repo lives at `~/shikumi-docker-labs`. To get updates later: `cd ~/shikumi-docker-labs && git pull`.

## How the labs work

- Each lab has its own folder under [`labs/`](labs/) with a `README.md` (goal, steps, checks, stretch challenge, cleanup) and every file the lab needs.
- You work in `~/labs/...` on the VM, not inside the clone. Step 0 of a lab copies its files there, for example `cp -a ~/shikumi-docker-labs/labs/04.1-first-dockerfile/app/. ~/labs/app/`. Re-running step 0 restores the tested version of every file.
- The project app (a small Flask API, later with Redis) grows across labs in `~/labs/app`. Labs build on each other in order; each README lists what it needs from earlier labs.
- Ports are published on 127.0.0.1 only. Learner resources are named and, where useful, labelled `course=shikumi`.
- Run each step's commands in order in the same terminal. A step that needs a second terminal says so.
- Nothing in this repo is a real secret. Token files are generated on your VM and are git-ignored.

## Lab index

| Lab | Module | Title | Time | Tested |
|---|---|---|---|---|
| [1.1](labs/01.1-install-docker-engine/) | M01 | Install Docker Engine and verify it | 30 min | partially verified |
| [2.1](labs/02.1-hello-world-exited/) | M02 | An image and a stopped container | 10 min | verified |
| [2.2](labs/02.2-container-states/) | M02 | Drive a container through every state | 20 min | verified |
| [3.1](labs/03.1-tags-digests-layers/) | M03 | Tags, digests, layers and platforms | 25 min | verified |
| [4.1](labs/04.1-first-dockerfile/) | M04 | Build, run and inspect the API | 25 min | verified |
| [5.1](labs/05.1-build-cache/) | M05 | Rebuild after a source edit | 15 min | verified |
| [5.2](labs/05.2-multi-stage-build/) | M05 | Multi-stage build with targets | 25 min | verified |
| [5.3](labs/05.3-multi-platform-buildx/) | M05 | A multi-platform image and a Buildx builder | 20 min | verified |
| [6.1](labs/06.1-local-registry/) | M06 | Run a local registry and push by tag and digest | 20 min | verified |
| [7.1](labs/07.1-bind-mounts-volumes/) | M07 | Bind-mounted page and a named volume | 25 min | verified |
| [8.1](labs/08.1-publish-ports/) | M08 | Publish a port and verify it | 20 min | verified |
| [8.2](labs/08.2-bridge-networks-dns/) | M08 | Names on a bridge, isolation and special networks | 25 min | verified |
| [9.1](labs/09.1-config-precedence/) | M09 | Configuration precedence and visibility | 20 min | verified |
| [10.1](labs/10.1-compose-api-redis/) | M10 | API + Redis with Compose | 30 min | verified |
| [10.2](labs/10.2-compose-profiles-watch/) | M10 | Profiles, overrides and watch | 30 min | verified |
| [11.1](labs/11.1-resource-limits/) | M11 | Configured limits, real throttling and an OOM kill | 20 min | verified |
| [12.1](labs/12.1-debug-a-container/) | M12 | Investigate a misbehaving container | 30 min | verified |
| [13.1](labs/13.1-rootless-docker/) | M13 | Rootless Docker for a second user (VM only) | 25 min | not verified |
| [13.2](labs/13.2-capabilities-read-only/) | M13 | Capabilities, no-new-privileges and a read-only root | 20 min | verified |
| [13.3](labs/13.3-build-and-runtime-secrets/) | M13 | Build secrets vs build args, and runtime secrets in Compose | 25 min | verified |
| [13.4](labs/13.4-image-scanning/) | M13 | Scan the course image | 20 min | partially verified |
| [14.1](labs/14.1-prune-selectively/) | M14 | Measure, then prune selectively | 15 min | verified |
| [15.1](labs/15.1-capstone-prod-deploy/) | M15 | Capstone: deploy the hardened stack from the registry | 45 min | verified |
| [16.1](labs/16.1-kubernetes-readiness/) | M16 | Kubernetes-readiness audit of the course image | 30 min | verified |

"Tested" means the steps were run end to end on a Debian 13 build machine with Docker 29.9.1. Partially verified or not verified labs need a real VM for some steps (systemd, re-login, rootless Docker, a Docker account); the lab's README says which.

## Modules

- **M00 · Course orientation and the lab VM** - How the course is organised, what each learner's VM needs, lab conventions and the command map.
- **M01 · Install and configure Docker Engine on Ubuntu / Debian** - Install from Docker's apt repository, verify, apply post-install steps, understand the docker group risk, contexts and daemon.json basics.
- **M02 · The container lifecycle** - Images vs containers, run/create/start/stop/kill/rm, foreground vs detached, exit codes, PID 1 and signals, restart policies.
- **M03 · Images, layers and the image store** - Pull by tag and digest, inspect layers and history, understand multi-platform indexes, the containerd image store, tags vs digests, save/load.
- **M04 · Dockerfile fundamentals** - Build context and .dockerignore, core instructions, CMD vs ENTRYPOINT, shell vs exec form, ARG vs ENV, LABEL, HEALTHCHECK, USER. Builds the course API image.
- **M05 · Build cache, multi-stage builds and BuildKit / Buildx** - How cache invalidation works, cache mounts, multi-stage builds with targets, Buildx builders, multi-platform images and Bake.
- **M06 · Registries, tagging and distribution** - Tagging strategy, Docker Hub login with access tokens, running a local registry, push/pull, digests and pull policies.
- **M07 · Storage: writable layer, volumes, bind mounts and tmpfs** - Where container data lives, named volumes vs bind mounts vs tmpfs, --mount syntax, read-only mounts, backup/restore and ownership pitfalls.
- **M08 · Networking** - Network namespaces, port publishing, default vs user-defined bridges and DNS, host/none networks, internal networks, aliases and firewall caveats.
- **M09 · Configuration: environment variables, build args and config files** - ENV vs ARG, -e and --env-file, precedence, labels, mounting config files, and why env vars are not secrets.
- **M10 · Docker Compose** - compose.yaml, services, networks and volumes, depends_on with health conditions, env interpolation and .env, profiles, overrides, watch, and the Compose lifecycle.
- **M11 · Resource limits and runtime controls** - cgroup v2 limits for memory, CPU and PIDs, OOM behaviour, live updates with docker update, and restart behaviour under failure.
- **M12 · Logging, debugging and observability** - docker logs options and log drivers, inspect with Go templates, exec, top, diff, cp, events, stats, health status, and debugging minimal images with shared namespaces.
- **M13 · Security** - Attack surface, rootless mode, non-root users, capabilities, no-new-privileges, read-only root filesystems, seccomp, image scanning (Docker Scout, Trivy), build secrets, runtime secrets, supply-chain hygiene.
- **M14 · Cleanup and pruning** - Measure disk usage, prune containers, images, volumes, networks and build cache selectively with filters and labels.
- **M15 · Production practices and capstone** - A production checklist (images, runtime, config, observability, operations) and a capstone that deploys the hardened API + Redis stack from a registry.
- **M16 · Bridge to Kubernetes** - What carries over from Docker to Kubernetes, what changes, a concept map from Docker/Compose to Kubernetes objects, and a Kubernetes-readiness audit of the course image. No Kubernetes installation.

## Copyright

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.

This is not open-source software. See [LICENSE](LICENSE). The repository is public so learners can clone it; no rights to reuse or redistribute are granted.
