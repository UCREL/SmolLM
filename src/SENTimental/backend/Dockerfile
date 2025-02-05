FROM node:latest

RUN mkdir /opt/node-server
WORKDIR /opt/node-server

COPY src/ /opt/node-server/
RUN npm install --production

EXPOSE 8888

ENTRYPOINT [ "node", "server.js" ]