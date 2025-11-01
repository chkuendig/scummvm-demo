FROM ubuntu:latest as builder

# install everything we need, which is a lot, since
# we launch a headless chromium to add games
RUN apt-get update
RUN apt-get install -y build-essential python-is-python3 git curl pkg-config libglib2.0-dev \
  libnspr4-dev libnss3-dev libdbus-1-dev libatk1.0-dev libatk-bridge2.0-dev libasound2-dev \
  libxkbcommon-dev libxcomposite-dev libxdamage-dev libxrandr-dev libgbm-dev libpango1.0-dev libcups2-dev
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN bash -c "source $NVM_DIR/nvm.sh && nvm install 24"

COPY .git /build/.git
COPY scripts /build/scripts
COPY scummvm /build/scummvm
COPY scummvm-icons /build/scummvm-icons
COPY package.json /build/package.json
COPY package-lock.json /build/package-lock.json

WORKDIR /build/scummvm

RUN echo Call configure

RUN ./dists/emscripten/build.sh configure \
  --enable-release --enable-all-engines --enable-plugins --default-dynamic \
  --enable-png --enable-ogg --enable-vorbis --enable-gif --enable-mpeg2 \
  --enable-freetype2 --enable-jpeg --enable-theoradec --enable-mad --enable-zlib 

RUN echo Build ScummVM 🔧

RUN ./dists/emscripten/build.sh make dist
RUN cp build-emscripten/scummvm.html build-emscripten/index.html
RUN cp AUTHORS COPYING LICENSES/* COPYRIGHT NEWS* README* build-emscripten/

RUN echo Update Icons 🖼️

WORKDIR /build
RUN ./scripts/update-icons.sh

RUN echo Add Games 🕹️

WORKDIR /build
RUN bash -c "source $NVM_DIR/nvm.sh && nvm use 24 && npm i"

# add your games to the /games folder before building
# they should be in subfolders, unpacked

COPY games /build/scummvm/build-emscripten/data/games

WORKDIR /build/scummvm
RUN ./dists/emscripten/build.sh dist

WORKDIR /build/scummvm/build-emscripten

# To skip game autodetection and use an already-crafted scummvm.ini,
#  copy your scummvm.ini to the games directory before building.
# It must have paths correct for the container, e.g.:
# 
# Added all my games to this repo, so an example game will be like:
#
# [lsl1sci]
# path=/home/user/git/scummvm-demo/games/lsl1sci
#
# But before building, the file should be modified like so:
#
# [lsl1sci]
# path=/data/games/lsl1sci


RUN /build/scripts/load_ini_or_autodetect.sh

WORKDIR /build/scummvm
RUN ./dists/emscripten/build.sh dist

FROM nginx:alpine-slim as runner

COPY --from=builder /build/scummvm/build-emscripten /usr/share/nginx/html

EXPOSE 80

CMD [ "nginx", "-g", "daemon off;" ]
