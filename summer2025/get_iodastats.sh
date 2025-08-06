#!/bin/bash
# Script to get IODA stats from the HPSS
# Usage: get_iodastats.sh <start_date> <end_date> <hpss_root> <output_directory>
# start_date and end_date should be in YYYYMMDDHH format

START=${START:-$1}
END=${END:-$2}
HPSS_ROOT=${HPSS_ROOT:-$3}
OUTDIR=${OUTDIR:-$4}

if [ -z "$START" ] || [ -z "$END" ] || [ -z "$HPSS_ROOT" ] || [ -z "$OUTDIR" ]; then
    echo "Usage: $0 <start_date> <end_date> <hpss_root> <output_directory>"
    exit 1
fi

# Create output directory if it does not exist
mkdir -p "$OUTDIR"

# Loop through the date range
current_date="$START"
cd "$OUTDIR" || exit 1
while [ "$current_date" -le "$END" ]; do
    # Construct the HPSS path
    PDY=$(echo "$current_date" | cut -c1-8)  # YYYYMMDD
    cyc=$(echo "$current_date" | cut -c9-10)  # HH
    #snow_stat="gdas.t${cyc}z.snow_iodastat.tgz"
    snow_stat="gdas.t${cyc}z.snowstat.tgz"
    hpss_path="$HPSS_ROOT/$current_date/gdas.tar"
    # gdas.20250217/00/products/snow/anlmon/gdas.t00z.snow_iodastat.tgz
    #hpss_file="gdas.${PDY}/${cyc}/products/snow/anlmon/${snow_stat}"
    hpss_file="gdas.${PDY}/${cyc}/analysis/snow/${snow_stat}"
    echo "htar -xvf $hpss_path $hpss_file"
    #htar -tvf $hpss_path
    htar -xvf $hpss_path $hpss_file
    if [ $? -ne 0 ]; then
        echo "Failed to extract $hpss_file from $hpss_path"
    else
        echo "Extracted $hpss_file to $OUTDIR"
    fi
    # extract the stat files
    cd "$OUTDIR/gdas.${PDY}/${cyc}/products/snow/anlmon" || exit 1
    tar -xzf ${snow_stat}
    if [ $? -ne 0 ]; then
        echo "Failed to extract ${snow_stat}"
    else
        echo "Extracted ${snow_stat} to $OUTDIR/gdas.${PDY}/${cyc}/products/snow/anlmon"
    fi
    # Move back to the output directory
    cd "$OUTDIR" || exit 1
    # Remove the tar file to save space
    rm -f "$hpss_file"
    # Increment the date by 6 hours
    current_date=$(date -d "${current_date:0:8} ${current_date:8:2} +6 hours" +%Y%m%d%H)
done