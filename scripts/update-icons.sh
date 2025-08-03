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
root_dir="$(pwd)"
scummvm_dir="$(pwd)/scummvm/"

#################################
# Add icons
#################################
echo "Adding icons"
icons_dir="${root_dir}/scummvm-icons/"
if [[ -d "$icons_dir" ]]; then
  mkdir -p "${scummvm_dir}/build-emscripten/data/gui-icons"
  echo "Adding files from icons repository "
  cp -r "${icons_dir}/default/icons" "${scummvm_dir}/build-emscripten/data/gui-icons/"
  cd "${icons_dir}"
  python3 gen-set.py
  echo "Manually patch games.xml and company.xml with metadata.json info"
  cd "${root_dir}/scripts"
  python3 update-icons-xml.py
  echo "add icons"
  cp -r "${icons_dir}/icons/"* "${scummvm_dir}/build-emscripten/data/gui-icons/icons/"
  echo "add xml"
  cp -r "$icons_dir/"*.xml "${scummvm_dir}/build-emscripten/data/gui-icons/"
  rm -f "${scummvm_dir}/build-emscripten/data/gui-icons.dat"
else
  echo "Icons repository not found"
fi

