import grib2io
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import datetime as dt
import os

ctrl_root="/scratch3/NCEPDEV/stmp/Cory.R.Martin/aug2025/snow-da-diffs/ctrl_grib2"
snowda_root="/scratch3/NCEPDEV/stmp/Cory.R.Martin/aug2025/snow-da-diffs/snowda_grib2"

start_date = dt.datetime(2024,10,25,0)
end_date = dt.datetime(2025,3,24,0)

nfiles = 0
fh = 'f000'
current_cycle = start_date
T_850 = np.zeros((721,1440))
snod = np.zeros((721,1440))
T_2m = np.zeros((721,1440))
mslp = np.zeros((721,1440))
while current_cycle <= end_date:
    print(current_cycle)
    # open the GRIB files
    exp_file = os.path.join(snowda_root,
                            f"gdas.{current_cycle.strftime('%Y%m%d')}",
                            current_cycle.strftime('%H'),
                            "products/atmos/grib2/0p25",
                            f"gdas.t{current_cycle.strftime('%H')}z.pgrb2.0p25.{fh}")
    grb_exp = grib2io.open(exp_file)
    ctrl_file = os.path.join(ctrl_root,
                             f"gdas.{current_cycle.strftime('%Y%m%d')}",
                             current_cycle.strftime('%H'),
                             "products/atmos/grib2/0p25",
                             f"gdas.t{current_cycle.strftime('%H')}z.pgrb2.0p25.{fh}")
    grb_ctl = grib2io.open(ctrl_file)
    # take the difference for certain fields
    # T850
    msg_exp = grb_exp.select(shortName='TMP', level='850 mb')[0]
    data_exp = msg_exp.data
    msg_ctl = grb_ctl.select(shortName='TMP', level='850 mb')[0]
    data_ctl = msg_ctl.data
    diff_T_850 = data_exp - data_ctl
    # SNOD
    msg_exp = grb_exp.select(shortName='SNOD', level='surface')[0]
    data_exp = msg_exp.data
    msg_ctl = grb_ctl.select(shortName='SNOD', level='surface')[0]
    data_ctl = msg_ctl.data
    diff_snod = data_exp - data_ctl
    # T2m
    msg_exp = grb_exp.select(shortName='TMP', level='2 m above ground')[0]
    data_exp = msg_exp.data
    msg_ctl = grb_ctl.select(shortName='TMP', level='2 m above ground')[0]
    data_ctl = msg_ctl.data
    diff_T_2m = data_exp - data_ctl
    # MSLP
    msg_exp = grb_exp.select(shortName='PRMSL', level='mean sea level')[0]
    data_exp = msg_exp.data
    msg_ctl = grb_ctl.select(shortName='PRMSL', level='mean sea level')[0]
    data_ctl = msg_ctl.data
    diff_mslp = data_exp - data_ctl
    # add this difference to the numpy array
    T_850 = T_850 + diff_T_850
    snod = snod + diff_snod
    T_2m = T_2m + diff_T_2m
    mslp = mslp + diff_mslp
    nfiles += 1
    current_cycle += dt.timedelta(hours=6)
    if current_cycle <= end_date:
        grb_ctl.close()
        grb_exp.close()
    else:
        lats, lons = msg_exp.grid()
        np.save('lons.npy', lons)
        np.save('lats.npy', lats)
        
# compute means
T_850_mean = T_850 / nfiles
np.save('T_850_mean.npy', T_850_mean)
snod_mean = snod / nfiles
np.save('snod_mean.npy', snod_mean)
T_2_mean = T_2m / nfiles
np.save('T_2m_mean.npy', T_2_mean)
mslp_mean = mslp / nfiles
np.save('mslp_mean.npy', mslp_mean)
# read means
T_850_mean = np.load('T_850_mean.npy')
snod_mean = np.load('snod_mean.npy')
T_2_mean = np.load('T_2m_mean.npy')
mslp_mean = np.load('mslp_mean.npy')

# set up figure(s)
fig = plt.figure(figsize=(15,10))
# Use PlateCarree projection for global data
ax = plt.axes(projection=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)
ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
ax.add_feature(cfeature.STATES, linewidth=0.1)

# Calculate statistics for color scaling
data_min = np.nanmin(T_850_mean)
data_max = np.nanmax(T_850_mean)
data_std = np.nanstd(T_850_mean)
data_mean = np.nanmean(T_850_mean)

# Set color limits as a function of the data
vmax = data_mean + 3 * data_std if data_std > 0 else data_max
vmin = data_mean - 3 * data_std if data_std > 0 else data_min

# Set extent based on region
if hasattr(ax, "set_extent"):
    ax.set_global()
contour = ax.pcolormesh(lons, lats, T_850_mean, vmin=vmin, vmax=vmax, cmap='coolwarm')
cbar = plt.colorbar(contour, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label("K")
ax.set_title(f'T_850 snowda-ctl mean {start_date}-{end_date}')
plt.savefig('T_850_diff.png', bbox_inches='tight')
plt.clf()

# set up figure(s)
fig = plt.figure(figsize=(15,10))
# Use PlateCarree projection for global data
ax = plt.axes(projection=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)
ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
ax.add_feature(cfeature.STATES, linewidth=0.1)

# Calculate statistics for color scaling
data_min = np.nanmin(snod_mean)
data_max = np.nanmax(snod_mean)
data_std = np.nanstd(snod_mean)
data_mean = np.nanmean(snod_mean)

# Set color limits as a function of the data
vmax = data_mean + 3 * data_std if data_std > 0 else data_max
vmin = data_mean - 3 * data_std if data_std > 0 else data_min

# Set extent based on region
if hasattr(ax, "set_extent"):
    ax.set_global()
contour = ax.pcolormesh(lons, lats, snod_mean, vmin=vmin, vmax=vmax, cmap='coolwarm')
cbar = plt.colorbar(contour, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label("")
ax.set_title(f'SNOD snowda-ctl mean {start_date}-{end_date}')
plt.savefig('snod_diff.png', bbox_inches='tight')
plt.clf()

# set up figure(s)
fig = plt.figure(figsize=(15,10))
# Use PlateCarree projection for global data
ax = plt.axes(projection=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)
ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
ax.add_feature(cfeature.STATES, linewidth=0.1)

# Calculate statistics for color scaling
data_min = np.nanmin(T_2_mean)
data_max = np.nanmax(T_2_mean)
data_std = np.nanstd(T_2_mean)
data_mean = np.nanmean(T_2_mean)

# Set color limits as a function of the data
vmax = data_mean + 3 * data_std if data_std > 0 else data_max
vmin = data_mean - 3 * data_std if data_std > 0 else data_min

# Set extent based on region
if hasattr(ax, "set_extent"):
    ax.set_global()
contour = ax.pcolormesh(lons, lats, T_2_mean, vmin=vmin, vmax=vmax, cmap='coolwarm')
cbar = plt.colorbar(contour, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label("")
ax.set_title(f'T2m snowda-ctl mean {start_date}-{end_date}')
plt.savefig('T2m_diff.png', bbox_inches='tight')
plt.clf()

# set up figure(s)
fig = plt.figure(figsize=(15,10))
# Use PlateCarree projection for global data
ax = plt.axes(projection=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)
ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
ax.add_feature(cfeature.STATES, linewidth=0.1)

# Calculate statistics for color scaling
data_min = np.nanmin(mslp_mean)
data_max = np.nanmax(mslp_mean)
data_std = np.nanstd(mslp_mean)
data_mean = np.nanmean(mslp_mean)

# Set color limits as a function of the data
vmax = data_mean + 3 * data_std if data_std > 0 else data_max
vmin = data_mean - 3 * data_std if data_std > 0 else data_min

# Set extent based on region
if hasattr(ax, "set_extent"):
    ax.set_global()
contour = ax.pcolormesh(lons, lats, mslp_mean, vmin=vmin, vmax=vmax, cmap='coolwarm')
cbar = plt.colorbar(contour, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label("")
ax.set_title(f'MSLP snowda-ctl mean {start_date}-{end_date}')
plt.savefig('mslp_diff.png', bbox_inches='tight')
plt.clf()