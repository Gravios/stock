FROM nginx:alpine

COPY templates/nginx.conf.template /etc/nginx/templates/

CMD ["/bin/sh", "-c", "envsubst < /etc/nginx/templates/nginx.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]
