# Faust Demo

This project demonstrates how faust can be used to build real time data computation services

## Usage

This application runs in a dockerised environment for local development.
Forwarding connections to kafka from the local host is difficult and error prone,
so we just run everything in the docker environment.
The dev docker container mounts this directory
so local file changes are also immediately in the docker container.

Example:

```bash
docker-compose up --build -d
docker-compose run --rm faust bash
```

You will then have a shell inside the container.
From here you can run commands as if you are running locally,
although changes to the projects dependencies will require rebuilding the docker image
(can be done by rerunning the `docker-compose up` command quoted above,
after regenerating the lock file).
To start the faust app, run:

```bash
faust -A faust_demo.app worker -l info
```

