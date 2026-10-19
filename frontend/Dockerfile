FROM node:22-alpine
WORKDIR /app/frontend
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ENV VITE_HOST=0.0.0.0
EXPOSE 5173
CMD ["npm", "run", "dev"]
