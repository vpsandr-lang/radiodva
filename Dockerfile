FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir flask flask-cors
EXPOSE 80 443
