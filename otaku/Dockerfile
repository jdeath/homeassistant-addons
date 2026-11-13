# otaku in a container, built and run by compose.yaml: the web interface on
# port 9600, the home folder in /data, the engines left on the host.
FROM python:3.13-slim

# OTAKU_WEB_PORT overrides a port set in config.toml, which would move the
# server off the one compose.yaml maps.
ENV OTAKU_COLOR=1 \
    OTAKU_HOME=/config \
    OTAKU_WEB_HOST=0.0.0.0 \
    OTAKU_WEB_PORT=9600 \
    OTAKU_TERMINAL_SERVE=on \
    PYTHONUNBUFFERED=1

# The checkout is mounted for the install, never copied in: the image
# carries the installed package alone.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
	rm -rf /var/lib/apt/lists/* && \
	git clone https://github.com/enclavum/otaku.git && \
    ls && \
	cd otaku && \
	pip install -e .

EXPOSE 9600

CMD ["otaku", "serve"]