FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build the app
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config if needed
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
