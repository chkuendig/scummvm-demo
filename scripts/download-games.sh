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



# exit when any command fails
set -e

_bundle_games="${1//,/ }"
root_dir="$(pwd)"
scummvm_dir="$(pwd)/scummvm/"
cd "${scummvm_dir}"
echo "Creating Games + Testbed Data"
mkdir -p "${scummvm_dir}/build-emscripten/data/games/"

echo ^\(${_bundle_games// /|}\)$
if [[ "playground3d" =~ $(echo ^\(${_bundle_games// /|}\)$) ]]; then
    mkdir -p "${scummvm_dir}/build-emscripten/data/games/playground3d"
fi

if [[ "testbed" =~ $(echo ^\(${_bundle_games// /|}\)$) ]]; then
    rm -rf "${scummvm_dir}/build-emscripten/data/games/testbed"
    cd "${scummvm_dir}/dists/engine-data"
    ./create-testbed-data.sh
    mv testbed "${scummvm_dir}/build-emscripten/data/games/testbed"
fi

echo "Fetching games: $_bundle_games"
if [ -n "$_bundle_games" ]; then
    echo "Fetching games: $_bundle_games"
    cd "${root_dir}"
    mkdir -p games/
    cd games/
    files=$(node --unhandled-rejections=strict --trace-warnings "${root_dir}/scripts/build-download_games.js" ${_bundle_games})
    for dir in "${scummvm_dir}/build-emscripten/games/"*/; do # cleanup games folder
      if [ "$(basename ${dir%*/})" != "testbed" ] && [ "$(basename ${dir%*/})" != "playground3d"  ]; then
        rm -rf "$dir"
      fi
    done
    for f in $files; do # unpack into games folder
      echo "Unzipping $f ..."
      unzip -q -n "$f" -d "${scummvm_dir}/build-emscripten/data/games/${f%.zip}"
      # some zip files have weird permissions, this fixes that:
      find "${scummvm_dir}/build-emscripten/data/games/${f%.zip}" -type d -exec chmod 0755 {} \;
      find "${scummvm_dir}/build-emscripten/data/games/${f%.zip}" -type f -exec chmod 0644 {} \;
    done
fi