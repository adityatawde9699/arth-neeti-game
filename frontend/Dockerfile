FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy project files
COPY . .

# Expose port
# 1. Build the static files
RUN npm run build

# 2. Install a simple static file server
RUN npm install -g serve

EXPOSE 5173

# 3. Serve the 'dist' folder
CMD ["serve", "-s", "dist", "-l", "5173"]
