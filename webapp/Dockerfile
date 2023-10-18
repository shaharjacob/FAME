FROM node:16

WORKDIR /webapp
COPY package.json ./
RUN npm install
RUN npm i -S react-loading-overlay --legacy-peer-deps
COPY . ./
RUN npm run-script build
RUN npm install -g serve