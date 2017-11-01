# Here's how to use imagemagick to display text
# Make a blank image
SIZE=320x240
TMP_FILE=/tmp/frame.png

# From: http://www.imagemagick.org/Usage/text/
convert tux.png -background lightblue \
		-size $SIZE \
      		label:'Dustin Kline' \
		-gravity Center \
      		$TMP_FILE

sudo fbi -noverbose -T 1 -a $TMP_FILE

# convert -list font

#convert tux.png -background khaki label: 'PENGUIN!!' \
#	-gravity Center -append labeledPenguin.png

#sudo  fbi -noverbose -T 1 -a labeledPenguin.png
