# Stage 1: Build
FROM node:23-alpine AS builder
RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm run docs:build

# Stage 2: Serve (unprivileged nginx, sem root)
FROM nginxinc/nginx-unprivileged:alpine
COPY --from=builder /app/docs/.vitepress/dist /usr/share/nginx/html
EXPOSE 8080
