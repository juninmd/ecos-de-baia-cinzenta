# Stage 1: Build
FROM node:22-alpine@sha256:fe4f6d74e20370acb04ad889077d14d0f64a9c8ea6a42bc60cddf1e844699914 AS builder
RUN npm install -g pnpm@10.30.3 && npm cache clean --force
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY patches/ ./patches/
RUN pnpm install --frozen-lockfile --config.store-dir=/tmp/pnpm-store
COPY . .
RUN NODE_OPTIONS=--max-old-space-size=4096 pnpm run docs:build

# Stage 2: Serve (unprivileged nginx, sem root)
FROM nginxinc/nginx-unprivileged:alpine@sha256:b5047b9b76845eac124358373c6852377c52e4b05834a47647e955dd91cb8f1e
COPY --from=builder /app/docs/.vitepress/dist /usr/share/nginx/html
EXPOSE 8080
