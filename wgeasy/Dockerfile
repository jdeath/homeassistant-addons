ARG BUILD_FROM
FROM ghcr.io/wg-easy/wg-easy

#VOLUME [ "/ssl" ]

RUN apk add -U --no-cache jq \
	&& sed -i 's/'\''wg-quick down wg0'\''/`wg-quick down ${WG_PATH}wg0.conf`/' /app/lib/WireGuard.js \
	&& sed -i 's/'\''wg-quick up wg0'\''/`wg-quick up ${WG_PATH}wg0.conf`/' /app/lib/WireGuard.js \
	&& sed -i 's/'\''wg syncconf wg0 <(wg-quick strip wg0)'\''/`wg syncconf wg0 <(wg-quick strip ${WG_PATH}wg0.conf)`/' /app/lib/WireGuard.js
	
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
