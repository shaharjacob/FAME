FROM node:lts

WORKDIR /webapp
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run-script build
RUN npm install -g serve