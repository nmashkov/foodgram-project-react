FROM nginx:1.19.3

COPY /infra/nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir /data

COPY /data/ingredients.csv /data

COPY /docs /docs