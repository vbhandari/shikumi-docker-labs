# Lab 13.3: Build secrets vs build args, and runtime secrets in Compose

**Module M13 · Security** · about 25 min · [Lab index](../../README.md#lab-index)

**Goal:** Prove an ARG leaks into image history while a secret mount does not, then give the API a runtime secret file through Compose.

## Before you start

- Lab 10.1
- Run the steps in order, in the same terminal, unless a step says otherwise.

## Files in this folder

- [`app/.dockerignore`](app/.dockerignore) → copied to `~/labs/app/.dockerignore`
- [`app/Dockerfile`](app/Dockerfile) → copied to `~/labs/app/Dockerfile`
- [`app/app.py`](app/app.py) → copied to `~/labs/app/app.py`
- [`app/compose.secrets.yaml`](app/compose.secrets.yaml) → copied to `~/labs/app/compose.secrets.yaml`
- [`app/compose.yaml`](app/compose.yaml) → copied to `~/labs/app/compose.yaml`
- [`app/requirements.txt`](app/requirements.txt) → copied to `~/labs/app/requirements.txt`
- [`m13/Dockerfile.leaky`](m13/Dockerfile.leaky) → copied to `~/labs/m13/Dockerfile.leaky`
- [`m13/Dockerfile.secret`](m13/Dockerfile.secret) → copied to `~/labs/m13/Dockerfile.secret`

## Steps

### Step 0: Copy this lab's files from the repo into your working folder (safe to re-run; it overwrites them with the tested versions).

```bash
mkdir -p ~/labs/app && cp -a ~/shikumi-docker-labs/labs/13.3-build-and-runtime-secrets/app/. ~/labs/app/
mkdir -p ~/labs/m13 && cp -a ~/shikumi-docker-labs/labs/13.3-build-and-runtime-secrets/m13/. ~/labs/m13/
ls -A ~/labs/m13
```

### Step 1: The anti-pattern: a token as ARG (Dockerfile.leaky, copied in step 0).

```bash
mkdir -p ~/labs/m13 && cd ~/labs/m13
docker build -f Dockerfile.leaky --build-arg API_TOKEN=s3cr3t-value -t leaky . 2>&1 | grep -i -A1 'warn' | head -4
docker history --no-trunc leaky | grep -o 'API_TOKEN=s3cr3t-value' | head -1
```

### Step 2: The fix: a secret mount (Dockerfile.secret, copied in step 0).

```bash
printf 's3cr3t-value' > token.txt
docker build -f Dockerfile.secret --secret id=api_token,src=token.txt -t safe .
docker run --rm safe cat /used.txt
docker run --rm safe ls /run/secrets 2>&1 ; echo "exit: $?"
docker history --no-trunc safe | grep -c s3cr3t-value
```

### Step 3: Runtime secret for the API via Compose (compose.secrets.yaml, copied in step 0).

```bash
cd ~/labs/app
mkdir -p secrets && printf 'shikumi-admin-%s' "$(date +%s)" > secrets/api_token.txt && chmod 644 secrets/api_token.txt
docker compose -f compose.yaml -f compose.secrets.yaml up -d --wait
curl -s -o /dev/null -w 'no token: %{http_code}\n' http://127.0.0.1:8000/admin
curl -sS -H "X-Admin-Token: $(cat secrets/api_token.txt)" http://127.0.0.1:8000/admin; echo
docker compose exec api ls -l /run/secrets/
docker inspect --format '{{json .Config.Env}}' shikumi-api-1 | grep -c shikumi-admin
```

## Checks (expected output)

- The leaky build prints a 'SecretsUsedInArgOrEnv' warning for API_TOKEN, and history reveals API_TOKEN=s3cr3t-value
- safe image: /used.txt says 'using token of length 12'
- ls /run/secrets in the final image fails ('No such file or directory'), and grep -c prints 0
- /admin returns 401 without the header and {"admin":"ok","hits":N} with it
- /run/secrets/api_token is present as a bind-mounted file; the env-var grep prints 0

## Stretch challenge

Use an environment-variable source instead of a file: 'API_TOKEN=... docker build --secret id=api_token,env=API_TOKEN ...'. Then make Compose build the 'safe' image with build.secrets (see docs).

## Cleanup

```bash
cd ~/labs/m13 && docker image rm leaky safe && rm -f token.txt
# keep ~/labs/app/secrets (ignored by .dockerignore) for M15
```

## Tested

Verified on 2026-10-19 (Debian 13 build machine, Docker Engine 29.9.1, Buildx v0.38.0, Compose v5.6.0, cgroup v2, containerd image store). BuildKit printed the SecretsUsedInArgOrEnv warning, and history leaked the ARG. The secret mount left no trace. Compose secret: 401 without the token, admin ok with it.

---

© 2026 Vinay Bhandari and Shikumi Labs. All rights reserved.
