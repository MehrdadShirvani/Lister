FROM node:18-alpine as build

WORKDIR /app

ARG VITE_API_URL
ENV VITE_API_URL=$REACT_APP_API_URL

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]