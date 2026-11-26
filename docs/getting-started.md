# Getting started

To run the site and Sanity Studio together without installing Node.js locally,
use [Docker Compose](docker.md):

```sh
docker compose up --build --watch
```

For native development, follow the steps below.

Use Node.js 24 and npm. The committed `package-lock.json` supplies the dependency
versions used by GitHub Actions.

```sh
git clone https://github.com/nicholasadamou/rebecca-richards-photography.git
cd rebecca-richards-photography
npm ci
npm run dev
```

Open the local URL printed by Astro, normally `http://localhost:4321`.
The portfolio includes the homepage, About Rebecca, services, contact details,
client albums, and individual album galleries.

## Content configuration

The site reads published albums from Sanity. To connect your own project, set
`PUBLIC_SANITY_PROJECT_ID` and `PUBLIC_SANITY_DATASET` in a local `.env` file.
Public datasets can be read without a token. Keep `SANITY_API_TOKEN` private;
content-import tools need it when writing to your own project.

The website and the separate `sanity-studio/` package have their own development
commands. Review the Studio configuration and album schema before editing or
importing content. See [development](development.md) for the available commands
and [the album scraper](../client-album-scraper/README.md) for the Python tooling.

## Build and preview

```sh
npm run build
npm run preview
```

The build generates social cards and writes the static website to `dist/`.
Album routes use the configured Sanity dataset at build time. The local preview
serves that output; restarting a development server does not rebuild it.

Hosting is currently disabled. The repository's CI still builds the site and
publishes a short-lived build artifact.

## Images and license

The code uses the [MIT License](../LICENSE). Photography belongs to Rebecca
Richards Photography and is excluded from that license. Keep the photography
notice with distributed copies and use images only with the appropriate rights.

[Development](development.md) · [Project overview](../README.md)
