FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js (via NodeSource), build tools and curl
RUN apt-get update && apt-get install -y \
    curl ca-certificates gnupg build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy app files
COPY package.json package-lock.json* ./
RUN npm install --production
COPY server.js ./
COPY public ./public

EXPOSE 3000

CMD ["node", "server.js"]