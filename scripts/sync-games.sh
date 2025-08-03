#!/bin/bash
#
# ScummVM is the legal property of its developers, whose names
# are too numerous to list here. Please refer to the COPYRIGHT
# file distributed with this source distribution.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

set -e # exit when any command fails

# adjust index to data baseurl
#jq '.games +=  {"baseUrl":env.DATA_BASEURL}' scummvm/build-emscripten/data/index.json > scummvm/build-emscripten/data/index.json.tmp && mv scummvm/build-emscripten/data/index.json.tmp scummvm/build-emscripten/data/index.json

# keep demos in sync and create games.json
python3 scripts/sync-games.py $@

# copy everything
mkdir -p scummvm/build-emscripten/ 
cp  assets/games.html scummvm/build-emscripten/

python3 scripts/sync-games-gen-json.py  $@
cp  games.json scummvm/build-emscripten/
