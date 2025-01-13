#!/bin/bash
set -e

# TODO: add two scripts, one to run the old process, one for the new
# TODO: Also add the testbed and playground3d to the json (manually or by using a previous json)


# fetch list of demos from google spreadsheet
#node demos_json.js
demo_folders=$(jq -r '.[:4] | .[].url | .[5:-4]' demos.json)

echo $demo_folders
mkdir -p games/
cd games/
rm -r */
games_dir=$(pwd)

# fetch list of games from ftp server (directory names)
# find ../scummvm/build-emscripten/data/games  -type d -depth 1 -exec basename {} \;
# create empty directory tree of files that exist
# download missing files
rsync -a -v --include='*/' --exclude='*' "christian@parklife.local:/srv/scummvm/games/" .
find . -type d -exec sh -c '(ls -p "{}"|grep />/dev/null)||echo "{}"' \; > existing_folders.txt
while IFS= read -r demo_folder; do
    echo "... $demo_folder ..."
    if [ ! -d "$demo_folder" ]; then 
        echo "$demo_folder does not exist."
        wget -nc "https://downloads.scummvm.org/frs/$demo_folder".zip -P "$demo_folder"
        cd "$demo_folder"
        filename=$(ls *.zip)
        unzip "$filename"
        rm "$filename"
        cd "$games_dir"
    else
        echo "$demo_folder already exists -  skipping"
    fi
done <<< "$demo_folders"

# generate index json
node ../build-make_http_index.js .

# delete empty index.json (folders that were already on the ftp)
while read p; do
  rm "$p/index.json"
done <existing_folders.txt
rm existing_folders.txt
# upload the games to the ftp server
rsync -a -v .  "christian@parklife.local:/srv/scummvm/games/"

# upload the demo json to the demo site