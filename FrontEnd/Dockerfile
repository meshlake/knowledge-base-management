# build front-end
# FROM --platform=linux/amd64 node:16 AS build-fe

# ADD . /app/
# WORKDIR /app

# RUN npm config set registry https://registry.npm.taobao.org
# RUN npm install --global pnpm
# RUN pnpm i --ignore-scripts

# CMD ["node", "server.js"]

# build image
FROM --platform=linux/amd64 nginx:1.21

# ADD . /app/
# WORKDIR /app

ENV AUTHORITY='127.0.0.1'

COPY ./dist /usr/share/nginx/html
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/docker-entrypoint.d/20-envsubst-on-templates.sh /docker-entrypoint.d/20-envsubst-on-templates.sh

# COPY --from=build-fe /app/dist /usr/share/nginx/html
# COPY --from=build-fe /app/nginx/nginx.conf /etc/nginx/nginx.conf
# COPY --from=build-fe /app/nginx/docker-entrypoint.d/20-envsubst-on-templates.sh /docker-entrypoint.d/20-envsubst-on-templates.sh