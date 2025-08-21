# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json for dependency installation
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Expose the port the React app runs on
EXPOSE 3000

# The command to start the development server
CMD ["npm", "start"]