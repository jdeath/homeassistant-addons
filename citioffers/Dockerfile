# Citi offer-activation tool — Docker image
#
# Build:
#   docker build -t citi-offers .
#
# Run (headless inside the container via Xvfb — no host display needed):
#   docker run --rm -it \
#     -v "$PWD/credentials.yaml:/config/credentials.yaml:ro" \
#     -v "$PWD/out:/config/out" \
#     citi-offers --activate
#
# Run (show the live browser window on the host's X/WSLg display):
#   docker run --rm -it \
#     -e DISPLAY=host \
#     -v /tmp/.X11-unix:/tmp/.X11-unix \
#     -v "$PWD/credentials.yaml:/config/credentials.yaml:ro" \
#     -v "$PWD/out:/config/out" \
#     citi-offers --activate

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    HOME=/root

# Chrome + Xvfb (off-screen display so the "headed" Chrome can run in a container)
# + the libraries a real Chrome binary needs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget ca-certificates \
        fonts-liberation fonts-noto-color-emoji \
        libasound2 libatk-bridge2.0-0 libatk1.0-0 libcairo2 libcups2 \
        libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libpango-1.0-0 \
        libnspr4 libnss3 \
        libcurl4 libvulkan1 \
        libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
        libxkbcommon0 libxrandr2 libxrender1 libxss1 libxtst6 \
        xdg-utils xauth x11-xserver-utils \
        xvfb x11-apps \
        python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install the official Google Chrome stable deb (arm64/amd64 auto via arch).
RUN set -eux; \
    arch=$(dpkg --print-architecture); \
    case "$arch" in \
      arm64) url="https://dl.google.com/linux/direct/google-chrome-stable_current_arm64.deb";; \
      amd64) url="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb";; \
      *) echo "unsupported arch: $arch" >&2; exit 1;; \
    esac; \
    wget -qO /tmp/chrome.deb "$url"; \
    apt-get install -y --no-install-recommends /tmp/chrome.deb || \
    (echo '[chrome] direct install failed, resolving deps...' && \
     apt-get update && apt-get install -y --no-install-recommends -f -y && \
     apt-get install -y /tmp/chrome.deb); \
    rm -f /tmp/chrome.deb; \
    which google-chrome || which google-chrome-stable

# Python deps
COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /requirements.txt

# Application
COPY citi_nodriver_login.py citi_activate_all_offers.py citi_session.py /app/
COPY run.sh /run.sh
RUN chmod a+x /run.sh

# Create /tmp/.X11-unix as WORLD-WRITABLE (1777) during the build (running as root).
# Xvfb hard-codes this socket path and only root can create it, so it MUST already
# exist at runtime. Making it 1777 means ANY non-root user (including Home
# Assistant's, whose UID may not be 1000) can use it without recreating it.
RUN mkdir -p /config/out /tmp/.chromium /tmp/.X11-unix \
    && chmod 1777 /tmp/.X11-unix /tmp /tmp/.chromium

# Non-root user so Chrome keeps its sandbox (root forces --no-sandbox, which
# Citi's ThreatMetrix bot gate fingerprints and 403s).
RUN useradd -m -u 1000 citi
USER citi
ENV HOME=/home/citi

# Where credentials + outputs live (mount here at runtime)
VOLUME /config
WORKDIR /config

ENTRYPOINT ["/run.sh"]
