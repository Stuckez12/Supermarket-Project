# DEV MODE: Single-stage
FROM node:20-alpine

WORKDIR /app

COPY src/frontend/customer_website/package*.json ./
RUN npm install

COPY src/frontend/customer_website ./

# TODO: Simplify installation of modules to potentially one line
RUN npm install react-hook-form
RUN npm install --save-dev style-loader
RUN npm install --save-dev css-loader
RUN npm install --save-dev @types/node
RUN npm install --save-dev react-router-dom
RUN npm install rollup@^3



RUN npm rebuild

EXPOSE 5173
CMD ["npm", "run", "dev"]
