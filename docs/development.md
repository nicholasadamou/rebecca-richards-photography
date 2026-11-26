# Development and local verification

Use `flox activate` for the locked Node.js 24 toolchain, then install both
committed dependency graphs with `npm ci` and `npm --prefix sanity-studio ci`.
Alternatively, [Docker Compose](docker.md) supplies the runtime and runs both
the website and Sanity Studio with live reload.

## Shared CI build

```sh
flox activate
npm ci
npm --prefix sanity-studio ci
npm run build
npm run sanity:build
actionlint
```

GitHub Actions runs these commands in the committed Flox environment on standard
GitHub-hosted Ubuntu runners for pushes to `master`, pull requests, and manual
dispatches. It then starts both Docker containers and builds Studio there too.
The site build generates Open Graph images before compiling Astro. Successful
runs retain `dist/` as a `website` artifact for seven days.

## Flox services

After installing both packages, run `flox services start` inside the activated
shell to start `site` and `studio`. They bind to the loopback interface at ports
4321 and 3333. Export `SITE_PORT` and `STUDIO_PORT` before starting services to
override them. Run `flox services stop` before changing ports, and check
`flox services status` or `flox services logs` when troubleshooting.

Flox supplies the native toolchain; Docker still uses its pinned Node.js image.
Install Docker separately for the container workflow. Flox activation does not
install npm dependencies, deploy Studio, or modify content.

## Commands

| Command                  | Purpose                                            |
| ------------------------ | -------------------------------------------------- |
| `npm run dev`            | Start the Astro development server                 |
| `npm run build`          | Generate social cards and build the static website |
| `npm run preview`        | Serve the built website locally                    |
| `npm run og:generate`    | Regenerate the Open Graph images                   |
| `npm run lint`           | Run the existing ESLint configuration              |
| `npm run format:check`   | Check formatting with Prettier                     |
| `npm run format`         | Apply Prettier formatting                          |
| `npm run sanity:dev`     | Start the separate Sanity Studio                   |
| `npm run sanity:build`   | Build Sanity Studio                                |
| `npm run sanity:deploy`  | Publish Sanity Studio when authorized              |
| `npm run test:sanity`    | Run the legacy authenticated CMS diagnostic        |
| `npm run migrate:sanity` | Import content into the configured Sanity project  |

The lint and formatting commands are additional local checks; they are not part
of the current hosted build gate. Content import and Studio publication change
remote state. Review their configuration and intended project before running them.
The legacy CMS diagnostic prints a token prefix, so keep its output private.

## Project layout

| Directory               | Responsibility                                         |
| ----------------------- | ------------------------------------------------------ |
| `src/pages/`            | Astro pages, album routes, and the Open Graph endpoint |
| `src/components/`       | Site navigation, album cards, galleries, and animation |
| `src/lib/`              | Sanity queries, image URLs, metadata, and analytics    |
| `src/styles/`           | Shared styling                                         |
| `public/`               | Static images, icons, and generated social cards       |
| `scripts/`              | Image generation, CMS diagnostics, and content import  |
| `sanity-studio/`        | Album schema and the separate CMS editor package       |
| `client-album-scraper/` | Python tools for collecting and processing album data  |

## Images and previews

The build preserves the homepage card and generates cards for About Rebecca,
services, contact, and album fallbacks. See [Open Graph images](OG-IMAGES.md) for templates and
[search metadata](SEO-IMPLEMENTATION.md) for page titles, structured data, and
sitemaps.

Existing interface previews are available as
[desktop](../.github/images/desktop-screenshot.png) and
[mobile](../.github/images/mobile-screenshot.png) screenshots.

For manual image preparation, ImageMagick can compress an authorized source image:

```sh
magick input.jpg -quality 85 -strip output.jpg
```

Photographs retain Rebecca Richards Photography's separate rights under the
[license notice](../LICENSE).

[Getting started](getting-started.md) · [Project overview](../README.md)
