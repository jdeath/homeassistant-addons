FROM node:22-alpine

ENV NODE_ENV=production
WORKDIR /app

RUN apk add --no-cache git \
	&& git clone https://github.com/DerKobe/PokerCrew.git . \
	&& npm ci --omit=dev && npm cache clean --force

USER node
EXPOSE 3000
CMD ["node", "server/index.js"]