# SENTimental - A tool for collecting human bilingual sentiment ratings

The recommended way to get started with SENTimental is to run it via `docker` or `podman` or other container-based system, and we include our `docker-compose.yml` as an example of running the basic stack. Note that this should be customised to match your own deployment.

The compose file will attempt to build the `frontend/` and `backend/` software, then run them both stitched together with a `traefik` reverse proxy in front of them.