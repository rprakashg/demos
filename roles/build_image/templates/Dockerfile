ARG REPO
ARG BASE = registry.access.redhat.com/ubi9/ubi9
FROM ${BASE}

RUN dnf -y install nginx  && dnf clean all

COPY ${REPO} /usr/share/nginx/html
COPY nginx.conf /etc/nginx.conf

EXPOSE 8080

CMD ["/usr/sbin/nginx", "-c", "/etc/nginx.conf"]

