FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built files from stage 1
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set environment variable for backend API URL
ENV VITE_API_URL=https://mealmind-production.up.railway.app

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 