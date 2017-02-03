#! /bin/sh
set +o noclobber
#
#   $1 = scanner device
#   $2 = friendly name
#

#   
#       100,200,300,400,600
#
resolution=300
device=$1
mkdir -p ~/brscan
if [ "`which usleep  2>/dev/null `" != '' ];then
    usleep 100000
else
    sleep  0.1
fi
DATE=$(date +%Y-%m-%d-%H-%M-%S)
output_dir=~/Dokumente/scans/"$DATE"
mkdir "$output_dir" && cd "$output_dir"

#echo "scan from $2($device) to $output_file"
echo "scanimage --device-name \"$device\" --resolution $resolution --format jpeg --source 'Automatic Document Feeder(left aligned,Duplex)' --batch='out%02d.jpg'"
scanimage --device-name "$device" --resolution $resolution --format jpeg --source 'Automatic Document Feeder(left aligned,Duplex)' --batch='out%02d.jpg'  2>/dev/null
echo "Scans in  $output_dir is created."

PDF="scan_${DATE}.pdf"
OCR="scan_${DATE}_ocr.pdf"
convert *.jpg $PDF
echo "Merged scans to $PDF, start OCR"

ocrmypdf --language deu --deskew --clean --rotate-pages --clean-final "$PDF" "$OCR"


