# Local development with Docker

Docker Compose runs the Astro site and Sanity Studio together. You need Docker
Desktop, or Docker Engine with Compose v2.32 or newer. Node.js and npm are
installed inside the images; you do not need them on the host.

## Start everything

From the repository root:

```sh
docker compose up --build --watch
```

- Site: <http://localhost:4321>
- Studio: <http://localhost:3333>

The first build installs each package's locked dependencies. Compose Watch syncs
source changes for live reload and rebuilds the appropriate image when its
`package.json` or `package-lock.json` changes. Dependencies stay inside the images,
so host `node_modules` directories cannot override the Linux dependencies.

Press Ctrl+C to stop. To remove the stopped containers and project network:

```sh
docker compose down
```

This does not delete content: albums and images remain in Sanity's hosted
Content Lake. These containers are a local development environment.

## Choose a project and dataset

The default is the existing `gwf79bj6` project and `production` dataset. Studio
edits affect that hosted dataset. To work against another existing dataset,
copy `.env.example` to `.env` and change these public settings:

```dotenv
PUBLIC_SANITY_PROJECT_ID=your-project-id
PUBLIC_SANITY_DATASET=development
SITE_PORT=4321
STUDIO_PORT=3333
```

Compose passes the same project and dataset to the website and Studio. Restart
Compose after changing `.env`; it is read by Compose, excluded from the images,
and not synced into containers. The public dataset can be read without an API
token. The Compose services do not receive API tokens from the host.

Studio uses Sanity's browser sign-in. Your account needs access to the selected
project. Do not put an editor token in `SANITY_STUDIO_*` variables: those values
are included in browser code. Existing content-import commands are separate from
this workflow and are never run automatically.

### Allow the Studio origin

In the selected project's API settings at <https://www.sanity.io/manage>, check
that `http://localhost:3333` is a CORS origin with **Allow credentials** enabled.
Add the exact browser origin you use if it is missing. If you change
`STUDIO_PORT`, allow the corresponding origin too. Opening `127.0.0.1` instead
of `localhost` also requires its own allowed origin.

## Port conflicts

Both services bind to the host's loopback interface. If their defaults are in
use, change `SITE_PORT` and `STUDIO_PORT` in `.env`, or set them for one run:

```sh
SITE_PORT=4381 STUDIO_PORT=3383 docker compose up --build --watch
```

Open `http://localhost:4381` and `http://localhost:3383` in this example. Container
ports stay at 4321 and 3333. Update the Sanity CORS origin for the Studio port.

## Health and troubleshooting

```sh
docker compose ps
docker compose logs site studio
```

Each service has an HTTP health check. The site probe reads a static icon, so
health checks do not repeatedly query Sanity. To start in the background and
wait for both servers:

```sh
docker compose up --build -d --wait --wait-timeout 180
```

Run `docker compose watch` in another terminal if you also want live source sync
in this mode. After changing a Dockerfile or Docker ignore rule, rerun
`docker compose up --build`.

If Studio loads but cannot sign in or edit content, check project access and
CORS settings. If the site has no albums, check that the selected dataset exists
and has published album documents. Internet access is required for Sanity data,
images, and sign-in. Local schema edits appear in Studio; published content is
fetched again on a site reload. Static production builds still require a rebuild
after content changes.

[Getting started](getting-started.md) · [Development](development.md)
