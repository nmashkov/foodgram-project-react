FROM nginx:1.19.3
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN mkdir /data
COPY /docs /usr/share/nginx/html/api/docs/
COPY ingredients.csv /data