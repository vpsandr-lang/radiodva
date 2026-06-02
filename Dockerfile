FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=5050

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip lame \
    && rm -rf /var/lib/apt/lists/*

# Copy app
WORKDIR /app
COPY . .

# Make directories writable
RUN mkdir -p /tmp/radio && chmod 777 /tmp/radio

# Expose port
EXPOSE 5050

# Run API + AI DJ broadcaster
CMD python3 -u run.py
