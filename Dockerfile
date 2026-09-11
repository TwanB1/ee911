# Site commercial EE911 — statique, servi par nginx derrière le proxy de
# l'infra (aucun port publié ; vhost www.ee911.eu → proxy_pass ee911-site:80).
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY site/ /usr/share/nginx/html/
