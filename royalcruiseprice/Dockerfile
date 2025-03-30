ARG BUILD_FROM
FROM python:3.12-slim
#FROM python:slim


ARG CHROME_VERSION="134.0.6998.165-1"
RUN apt-get update -y && \
	apt-get install -y wget xvfb --no-install-recommends && \
	wget -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb && \
	apt-get install -y --no-install-recommends /tmp/chrome.deb && \
	rm /tmp/chrome.deb && \
	pip install --no-cache-dir --root-user-action=ignore apprise selenium

# setting display environment stuff
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

WORKDIR /app
COPY run.sh ./
COPY entrypoint.sh ./
COPY CruisePriceCheck.py ./
COPY chromedriver /usr/bin/
RUN chmod a+x ./*.sh /usr/bin/chromedriver

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