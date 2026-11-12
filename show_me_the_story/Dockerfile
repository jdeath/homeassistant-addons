FROM ghcr.io/home-assistant/base:3.24

ARG TARGETARCH
ARG BUILD_VERSION
WORKDIR /
RUN if [ "${TARGETARCH}" = "amd64" ]; then \
        echo "Running AMD64 specific setup..." && \
        curl -fL -o story.tar.gz https://github.com/Nigh/show-me-the-story/releases/download/${BUILD_VERSION}/show-me-the-story-${BUILD_VERSION}-linux-amd64.tar.gz && \
		tar -zxvf story.tar.gz && \
		chmod a+x /show-me-the-story; \
    elif [ "${TARGETARCH}" = "arm64" ]; then \
        echo "Running ARM64 specific setup..." && \
        curl -fL -o story.tar.gz https://github.com/Nigh/show-me-the-story/releases/download/${BUILD_VERSION}/show-me-the-story-${BUILD_VERSION}-linux-arm64.tar.gz && \
		tar -zxvf story.tar.gz && \ 
		chmod a+x /show-me-the-story; \
    else \
        echo "Running fallback setup for $TARGETARCH..."; \
    fi
	
CMD ["/show-me-the-story", "/config"]
