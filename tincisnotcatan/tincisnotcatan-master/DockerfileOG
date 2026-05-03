FROM ghcr.io/hassio-addons/base

RUN mkdir /data
WORKDIR /data

RUN apk update
RUN apk fetch openjdk8
RUN apk add openjdk8 bash maven
ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk

ADD ./tincisnotcatan-master .
RUN ./build.sh
EXPOSE 4567/tcp
CMD ./run
