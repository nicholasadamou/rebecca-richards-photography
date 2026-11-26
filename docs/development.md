# Development and local verification

Use Node.js 24 and install the committed dependency graph with `npm ci`.
Alternatively, [Docker Compose](docker.md) supplies the runtime and runs both
the website and Sanity Studio with live reload.

## Shared CI build

```sh
npm ci
npm run build
```

GitHub Actions runs these commands on standard GitHub-hosted Ubuntu runners for
pushes to `master`, pull requests, and manual dispatches. The build generates
Open Graph images before compiling the Astro website. Successful runs retain
`dist/` as a `website` artifact for seven days.

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
