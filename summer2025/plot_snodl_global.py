import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import os

def plot_global_snodl(sfcanl_prefix, oro_prefix):
    plt.figure(figsize=(14, 8))
    ax = plt.axes(projection=ccrs.Robinson())
    ax.set_global()
    ax.coastlines()
    ax.set_title("FV3 Snow Depth Liquid (snodl) - Global Map")

    # Loop over all 6 tiles
    for tile in range(1, 7):
        sfcanl_file = f"{sfcanl_prefix}tile{tile}.nc"
        oro_file = f"{oro_prefix}tile{tile}.nc"

        if not (os.path.exists(sfcanl_file) and os.path.exists(oro_file)):
            print(f"Missing file for tile {tile}: {sfcanl_file} or {oro_file}")
            continue

        ds_sf = xr.open_dataset(sfcanl_file)
        ds_oro = xr.open_dataset(oro_file)

        lon = ds_oro['geolon'].values
        lat = ds_oro['geolat'].values
        snodl = ds_sf['snodl'][0, :, :].values

        # Mask invalid data if needed
        snodl = np.ma.masked_invalid(snodl)

        # Plot each tile's data
        pcm = ax.pcolormesh(lon, lat, snodl, cmap='bwr', shading='auto', transform=ccrs.PlateCarree(), vmin=-1000, vmax=1000)

    plt.colorbar(pcm, ax=ax, orientation='horizontal', pad=0.05, label='Snow Liquid (mm)')
    plt.savefig('plot.png')

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python plot_snodl_global.py <sfcanl_data_prefix> <oro_data_prefix>")
        print("Example: python plot_snodl_global.py 20250101.000000.sfcanl_data. C384.mx025_oro_data.")
        sys.exit(1)
    sfcanl_prefix = sys.argv[1]
    oro_prefix = sys.argv[2]
    plot_global_snodl(sfcanl_prefix, oro_prefix)
