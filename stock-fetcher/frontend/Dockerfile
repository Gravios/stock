
FROM node:22

WORKDIR /app

COPY ./package.json ./
COPY ./package-lock.json ./

RUN npm install

COPY . .
COPY ./app/App.jsx ./app/App.jsx
COPY ./app/index.jsx ./app/index.jsx

CMD ["npm", "start"]

