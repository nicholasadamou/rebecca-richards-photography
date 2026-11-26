FROM node:24-bookworm-slim@sha256:873f586f3794f52281bd039bf02c048a0be08fde619338f9941bad1eb6b34530 AS base

WORKDIR /app
RUN chown node:node /app
USER node

FROM base AS site
COPY --chown=node:node package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY --chown=node:node . .
EXPOSE 4321
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4321"]

FROM base AS studio
COPY --chown=node:node sanity-studio/package.json sanity-studio/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY --chown=node:node sanity-studio/ ./
EXPOSE 3333
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
