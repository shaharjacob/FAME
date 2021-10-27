FROM node:latest

WORKDIR /webapp
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
