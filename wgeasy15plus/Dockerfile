FROM ghcr.io/wg-easy/wg-easy:15.2.2

RUN apk add --no-cache nginx jq

COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]
