#!/bin/sh
# set -x

# Definitions
IMAGE_EXT='bmp|gif|jpg|jpeg|png|raw|tiff|svg'
VIDEO_EXT='webm|mkv|ogg|gif|gifv|avi|wmv|mp4'
MEDIA_EXT="$IMAGE_EXT|$VIDEO_EXT"

# Settings
VENV_PATH="$HOME/Github/venv"
DOWNLOAD_FOLDER='Results'
EXTENSIONS=$IMAGE_EXT

Reddit () {
	source $(printf "$VENV_PATH/bin/activate")
	scrapy crawl reddit -a subreddit=hatsune -a unix_time=1548979200
	deactivate
}

Download () {
	mkdir -p $DOWNLOAD_FOLDER
	for x in $(cat reddit.csv | cut -d ',' -f 5 | grep -E $(printf "\.($EXTENSIONS)\$") | sed 's/\(http\)\([^s]\)/\1s\2/'); do
		(
			destination="$DOWNLOAD_FOLDER/$(printf "$x" | sha512sum | awk '{print $1 = $1}')"
			curl -o $destination $x
			newdest="$DOWNLOAD_FOLDER/$(sha512sum $destination | awk '{print $1 = $1}')"
			mv $destination $newdest
		) > /dev/null 2>&1 &
	done
	printf "Downloading, please wait...\n"
	wait
	printf "Done!\n"
}

# Main
Reddit
Download
exit 0
