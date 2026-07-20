FROM node:22.17.1-alpine3.22 AS builder
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html tsconfig.json vite.config.mjs ./
COPY src ./src
RUN npm run build

FROM nginx:1.28.0-alpine3.21
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /build/dist /usr/share/nginx/html
USER nginx
EXPOSE 8080
