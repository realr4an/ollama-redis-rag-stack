FROM node:20-alpine AS build
WORKDIR /app
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
COPY package.json pnpm-lock.yaml tsconfig.json vite.config.ts vitest.setup.ts index.html ./
COPY src ./src
RUN corepack enable && pnpm install --frozen-lockfile && pnpm build

FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
