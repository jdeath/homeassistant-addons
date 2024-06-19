ARG BUILD_FROM
FROM python:slim

RUN apt-get update -y && \
	apt-get install -y git wget xvfb --no-install-recommends && \
	wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
	apt-get install -y --no-install-recommends /tmp/chrome.deb && \
	rm /tmp/chrome.deb && \
	google-chrome --version && \
	mkdir /app && cd /app && \
	git clone https://github.com/jdeath/MS-Rewards-Farmer.git ./ && \
 	pip install --no-deps --no-cache-dir --root-user-action=ignore -r requirements.txt && \
 	pip install --no-deps --no-cache-dir --root-user-action=ignore --upgrade -r requirements.txt 

# setting display environment stuff
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

WORKDIR /app
COPY run.sh ./
COPY entrypoint.sh ./
RUN chmod a+x ./*.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["/app/run.sh"]

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
