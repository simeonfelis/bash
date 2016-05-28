#!/bin/bash
#set -x

# will add a smaller version of all videos from a given path
# videos will be searched recursively
# videos need the file ending .mp4

# sets WDITH and HEIGHT and SIZE
# return 0 on landscape
# returns 1 on portrait
# returns -1 on errors (ffprobe error or WIDTH/HEIGHT invalid)
get_orientation () {
    WIDTH=0
    HEIGHT=0
    eval $(ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width "${1}")
    if [[ $? -ne 0 ]]; then
        return -1
    fi
    SIZE=${streams_stream_0_width}x${streams_stream_0_height}
    WIDTH=$streams_stream_0_width
    HEIGHT=$streams_stream_0_height
    if [[ $WIDTH -eq 0 ]]; then
        echo "Invalid resolution for ${1}"
        return -1
    elif [[ $HEIGHT -eq 0 ]]; then
        echo "Invalid resolution for ${1}"
        return -1
    fi
    export SIZE
    export WIDTH
    export HEIGHT

    if [[ $WIDTH -ge $HEIGHT ]]; then
        return 0
    else
        return 1
    fi
}


get_smallname () {
    FULLPATH="$1"
    EXTENSION="${FULLPATH##*.}"

    echo "${FULLPATH%.*}_small.${EXTENSION}"
}

is_smallname () {
    FILENAME="${1%.*}" # remove extension
    SUFFIX="${FILENAME##*_}" # keep all after last _
    if [[ "${SUFFIX}" == "small" ]]; then
        return 0
    else
        return 1
    fi
}

resize_vid () {
    VIDFILE="$1"
    if [[ ! -f "${VIDFILE}" ]]; then
        echo "Warning: '$VIDFILE' is not a regular file. Ignoring"
        return -1
    fi

    OUTFILE=$(get_smallname "${VIDFILE}")
    if [[ -f "${OUTFILE}" ]]; then
        echo "$VIDFILE: small version already present, skipping"
        return 0
    fi

    get_orientation "${VIDFILE}"
    ORIENT=$?
    if [[ $ORIENT -lt 0 ]]; then
        echo "error determining orientation and size of $VIDFILE, skipping"
        return -1
    fi
    if [[ -z $WIDTH ]]; then
        echo "WIDTH is invalid: $WIDTH"
        return -1
    fi

    #ffmpeg -n -loglevel quiet -i "${VIDFILE}" -r 25 -c:a copy -vf scale=$(($WIDTH/2)):-1 "${OUTFILE}" > /dev/null 2>&1
    #ffmpeg -n -loglevel error -i "${VIDFILE}" -r 25 -c:a copy -vf scale=$(($WIDTH/2)):-1 "${OUTFILE}"
    # ffmpeg sucks stdin, leading the outer loop to break
    ffmpeg -n -loglevel quiet -i "${VIDFILE}" -c:a copy -vf scale=$(($WIDTH/3)):-1 "${OUTFILE}" < /dev/null
}

print_size () {
    if [[ ! -f "${1}" ]]; then
        echo "error: $1 not found"
        return
    elif [[ ! -f "${2}" ]]; then
        echo "error: $2 not found"
        return
    fi
    S1=$(stat --format=%s "${1}")
    S2=$(stat --format=%s "${2}")

    GB=$((1024*1024*1024))
    MB=$((1024*1024))
    KB=1024
    if [[ $S1 -ge $GB ]]; then
        S1=$(($S1/$GB))
        S1=$(echo $S1 GB)
    elif [[ $S1 -ge $MB ]]; then
        S1=$(($S1/$MB))
        S1=$(echo $S1 MB)
    elif [[ $S1 -ge $KB ]]; then
        S1=$(($S1/$KB))
        S1=$(echo $S1 KB)
    else
        S1=$(echo $S1 B)
    fi
    if [[ $S2 -ge $GB ]]; then
        S2=$(($S2/$GB))
        S2=$(echo $S2 GB)
    elif [[ $S2 -ge $MB ]]; then
        S2=$(($S2/$MB))
        S2=$(echo $S2 MB)
    elif [[ $S2 -ge $KB ]]; then
        S2=$(($S2/$KB))
        S2=$(echo $S2 KB)
    else
        S2=$(echo $S2 B)
    fi
    echo "Before: $S1; small: $S2 ($2)"
}

SPATH="$1"

if [[ ! -d "${SPATH}" ]]; then
    echo "Please provide a path to scan for videos"
    exit -1
fi

TOTAL=0
CURRENT=0

while read -d $'\0' X; do
    is_smallname "${X}"
    if [[ $? -ne 0 ]]; then
        TMP=$(get_smallname "${X}")
        if [[ ! -f "${TMP}" ]]; then
            TOTAL=$(($TOTAL+1))
        fi
    fi
done < <(find "${SPATH}" -type f -iname "*.mp4" -print0)
unset X
unset TMP

toconvert=$(find "${SPATH}" -type f -iname "*.mp4")
echo "to convert: $toconvert"

while read -d $'\0' VID; do
    is_smallname "${VID}"
    ret=$?
    if [[ $ret -ne 0 ]]; then
        OUT=$(get_smallname "${VID}")
        if [[ ! -f "${OUT}" ]]; then
            CURRENT=$(($CURRENT+1))
            echo "${CURRENT}/${TOTAL}: $VID to $OUT"
            resize_vid "${VID}"
            print_size "${VID}" "${OUT}"
        else
            echo "File ${OUT} already exists"
        fi
    else
        echo "is_smallname for ${VID} returned $ret"
    fi
done < <(find "${SPATH}" -type f -iname "*.mp4" -print0)


