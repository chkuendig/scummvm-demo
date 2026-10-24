#!/bin/sh

BUILDDIR=/build/scummvm/build-emscripten
DIR=${BUILDDIR}/data/games

if [ -f ${DIR}/scummvm.ini ]; then
    mv ${DIR}/scummvm.ini ${BUILDDIR}
else
    source $NVM_DIR/nvm.sh
    nvm use default
    node /build/scripts/autodetect-games.js
fi