ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add curl unzip npm python3 nginx \
    && curl -LO https://github.com/Lattyware/massivedecks/archive/refs/tags/v2.6.0.zip \
    && unzip v2.6.0.zip \
    && rm v2.6.0.zip \
    && apk del curl unzip \
	&& cd massivedecks-2.6.0/server/ \
	&& npm install typescript \
	&& npm run build \
	&& cd /massivedecks-2.6.0/client/ \
	&& npm install webpack-cli \
	&& npm run build \
	&& cp -r dist /usr/share/nginx/html/ \
	&& sed -i 's/server:8081/localhost:8081/' nginx.conf \ 
	&& cp nginx.conf /etc/nginx/nginx.conf
	
	
EXPOSE 8080
EXPOSE 8081

COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]

### LABELS
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="jdeath (https://github.com/jdeath)" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Home Assistant Add-ons" \
    org.opencontainers.image.authors="jdeath (https://github.com/jdeath)" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/jdeath" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
