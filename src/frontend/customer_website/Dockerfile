# DEV MODE: Single-stage
FROM node:20-alpine

WORKDIR /app

COPY src/frontend/customer_website/package*.json ./
RUN npm install

COPY src/frontend/customer_website ./

EXPOSE 5173
CMD ["npm", "run", "dev"]
