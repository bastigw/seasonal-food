# Stage 1: bake the seasonal produce data (all countries x all months) into a
# single JSON file, so the shipped app needs no backend and no runtime API.
FROM python:3.12-slim AS data
WORKDIR /build
COPY app ./app
COPY scripts ./scripts
COPY eufic_seasonal_produce_matrix.json .
RUN python3 scripts/generate_data.py

# Stage 2: build the static Vue app.
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend ./
COPY --from=data /build/frontend/src/data/seasonal.json ./src/data/seasonal.json
RUN npm run build

# Stage 3: serve the built static files. No env vars, no volumes.
FROM nginx:alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
