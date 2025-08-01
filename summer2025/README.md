# Summer 2025

### Load GRIB2 plotting environment
on Ursa
```
module use /scratch3/NCEPDEV/da/Cory.R.Martin/python/modulefiles
module load grib2_files
```

### Get GRIB2 file content
```
module load wgrib2
wgrib2 pgbf00.gdas.2024122500.grib2
```

### Run script example
```
python plot_grib2.py ../../snow-da-diffs/gdas.20241225/00/products/atmos/grib2/0p25/gdas.t00z.pgrb2.0p25.f000 --variable SNOD --level surface --output snod_conus.png --title-prefix 'snow 2dvar' --region CONUS
```
