FROM node:latest AS build

WORKDIR /src

COPY . /src/

RUN npm install && npm run build

FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY proxy.conf /etc/nginx/include/proxy.conf

COPY --from=build /src/dist/ /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]