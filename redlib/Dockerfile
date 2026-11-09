FROM ghcr.io/home-assistant/base:3.24

ARG TARGETARCH

USER root
WORKDIR /
RUN if [ "${TARGETARCH}" = "amd64" ]; then \
        echo "Running AMD64 specific setup..." && \
        curl -fL -o redlib https://github.com/Nachtalb/redlib/releases/latest/download/redlib-x86_64-unknown-linux-musl;\
    elif [ "${TARGETARCH}" = "arm64" ]; then \
        echo "Running ARM64 specific setup..." && \
        curl -fL -o redlib https://github.com/Nachtalb/redlib/releases/download/latest/redlib-aarch64-unknown-linux-musl; \
    else \
        echo "Running fallback setup for $TARGETARCH..."; \
    fi

COPY rootfs/ /
RUN chmod a+x /redlib
RUN chmod a+x /run.sh
RUN chmod a+x /custom.sh

ENTRYPOINT /run.sh
