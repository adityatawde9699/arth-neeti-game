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
EXPOSE 5173

# Run Vite dev server with host binding for Docker
CMD ["npm", "run", "dev", "--", "--host"]
