import argparse
import grib2io
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

def plot_grib(file: str,
              variable: str,
              level: str,
              output_file: str = None,
              title_prefix: str = "GRIB file",
              region: str = "global") -> None:
    """
    Plot the values in a GRIB file for a specified variable.
    
    Args:
        file (str): Path to GRIB file
        variable (str):  variable name (e.g., 'dust_bin1', 'sulfate', etc.)
        level (int): Level index to plot (0-based)
        output_file (str): Output filename for the plot
        title_prefix (str): Prefix for the plot title
        region (str): Region to plot ('global' or 'CONUS')
    """
    # open the grib file for reading
    grb = grib2io.open(file)

    # get grid information from first message of file, assumes grids are the same
    first_msg = grb[0]
    lats, lons = first_msg.grid()
    msg = grb.select(shortName=variable, level=level)[0]
    valid_time = first_msg.validDate
    lead_time = first_msg.leadTime
    data = msg.data

    # Create the plot
    fig = plt.figure(figsize=(15, 10))
    
    # Use PlateCarree projection for global data
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
    ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
    if region == "CONUS":
        ax.add_feature(cfeature.STATES, linewidth=0.3)
    
    # Calculate statistics for color scaling
    data_min = np.nanmin(data)
    data_max = np.nanmax(data)
    data_std = np.nanstd(data)
    data_mean = np.nanmean(data)

    # Set color limits as a function of the data
    vmax = data_mean + 3 * data_std if data_std > 0 else data_max
    vmin = data_mean - 3 * data_std if data_std > 0 else data_min

    # Create contour plot
    levels_plot = np.linspace(vmin, vmax, 21)
    # Set extent based on region
    if hasattr(ax, "set_extent"):
        if region == "CONUS":
            # Approximate CONUS extent: [west_lon, east_lon, south_lat, north_lat]
            ax.set_extent([-130, -65, 23, 50], crs=ccrs.PlateCarree())
        else:
            # Global extent
            ax.set_global()

    contour = ax.contourf(lons, lats, data, levels=levels_plot, cmap='viridis', extend='both')
    cbar = plt.colorbar(contour, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label(msg.units)
    ax.set_title(f'{title_prefix}: {variable} at {level} (Valid: {valid_time}, Lead: {lead_time})')

    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
    else:
        plt.show()

def main():
    """
    Main function with command line argument parsing.
    """
    parser = argparse.ArgumentParser(description='Plot variable from a GRIB file')
    parser.add_argument('file', help='Path to GRIB file')
    parser.add_argument('--variable', '-v', default='TMP', 
                       help='Variable to plot (default: TMP)')
    parser.add_argument('--level', '-l', default='1000 mb', 
                       help='Level to plot (default: 1000 mb)')
    parser.add_argument('--output', '-o', 
                       help='Output filename (default: show plot)')
    parser.add_argument('--output-dir', default='.',
                       help='Output directory for multiple plots (default: current directory)')
    parser.add_argument('--title-prefix', default='Aerosol',
                       help='Prefix for plot title')
    parser.add_argument('--region', choices=['global', 'CONUS'], default='global',
                       help='Region to plot (default: global)')
    
    args = parser.parse_args()

    plot_grib(args.file, args.variable, args.level, args.output, args.title_prefix, args.region)



if __name__ == "__main__":
    main()
