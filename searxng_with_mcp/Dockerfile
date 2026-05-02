#############
ARG BUILD_FROM
ARG BUILD_ARCH
ARG BUILD_VERSION

FROM $BUILD_FROM

COPY rootfs/ /
COPY server.py /

RUN python -m ensurepip --upgrade
RUN pip3 install --no-cache-dir fastmcp httpx python-dotenv fastapi

RUN chmod a+x /run.sh

ENTRYPOINT ["/run.sh"]

LABEL \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION}