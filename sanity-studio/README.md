# Sanity Studio

The CMS editor for Rebecca Richards Photography manages client albums and their
images in Sanity's hosted Content Lake. Running Studio locally does not create a
local database or copy the dataset.

## Docker

From the repository root:

```sh
docker compose up --build --watch
```

Open <http://localhost:3333> and sign in with a Sanity account that has project
access. The website runs at <http://localhost:4321>. See
[Docker setup](../docs/docker.md) for shared project settings, CORS, live reload,
and port overrides. No editor API token is needed for Studio.

## Native development

From the repository root, activate Flox for Node.js 24 and npm:

```sh
flox activate
npm --prefix sanity-studio ci
npm run sanity:dev
```

Studio defaults to project `gwf79bj6`, dataset `production`. To use another
existing dataset natively, create a gitignored `sanity-studio/.env`:

```dotenv
SANITY_STUDIO_PROJECT_ID=your-project-id
SANITY_STUDIO_DATASET=development
```

The CLI and Studio configuration read the same values. These variables are
public browser configuration; do not add credentials to them. For Docker, use
the root `.env` public settings instead, as described in the Docker guide.

The Studio's browser origin must be allowed in the project's CORS settings with
credentials enabled. See <https://www.sanity.io/manage>.

## Album schema

`album-schema.js` defines the `album` document:

- Title, slug, album type, session date, and description
- Cover image and gallery images with alt text and hotspot support
- Published and featured flags
- Session location and client names

Only published albums appear on the website; the homepage selects featured
albums. Schema or configuration edits reload Studio. Publishing content changes
the selected hosted dataset; reload the local site to fetch changes. Static
builds need to be rebuilt after content changes.

## Build and content imports

```sh
npm run sanity:build
```

This builds the editor into `sanity-studio/dist/`. Docker's development service
does not publish Studio or import content automatically.

The separate root `npm run migrate:sanity` command uploads images and creates
album documents in its configured project. Review its source and credentials
before using it. It is not required to start the editor or browse existing
content. `npm run sanity:deploy` publishes Studio and should only be run when
publication is intended.

[Getting started](../docs/getting-started.md) · [Development](../docs/development.md)
