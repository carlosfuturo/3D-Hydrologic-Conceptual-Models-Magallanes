import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.interpolate import griddata
import rasterio
from rasterio.mask import mask as rio_mask
from scipy.ndimage import zoom

BASE = "/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes"
BASIN_SHP = BASE + "/01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp"
BOT_SHP   = BASE + "/03 SIG Magallanes/propsBOT_Vertientes_Proj.shp"
DEM_PATH  = BASE + "/02 PyScripts Magallanes/DEM_Copernicus_30m/mosaicos/DEM_Cop30_Penitente_UTM19S.tif"

basins = gpd.read_file(BASIN_SHP)
poly = basins.loc[basins["NOMBRE"] == "RIO PENITENTE", "geometry"].iloc[0]
xmin, ymin, xmax, ymax = poly.bounds

# Load full BOT layer
gdf = gpd.read_file(BOT_SHP)

# Try several buffer sizes
buffers = [0, 300, 600, 1200]
fig, axes = plt.subplots(2, 2, figsize=(14, 14))
axes = axes.ravel()

# Load DEM mask to show actual basin cells
with rasterio.open(DEM_PATH) as src:
    raw, _ = rio_mask(src, [poly], crop=True, nodata=-9999)
    elev_raw = np.flipud(raw[0].astype("float32"))
    elev_raw[elev_raw == -9999] = np.nan
rows, cols = elev_raw.shape
N = 80
zoom_r = N / max(rows, cols)
from scipy.ndimage import zoom as nzoom
elev_m = nzoom(elev_raw, zoom_r, order=1, prefilter=False)
nan_w  = nzoom(np.where(np.isnan(elev_raw), 0.0, 1.0).astype("float32"), zoom_r, order=0)
elev_m[nan_w < 0.5] = np.nan
xi = np.linspace(xmin, xmax, elev_m.shape[1])
yi = np.linspace(ymin, ymax, elev_m.shape[0])
XX, YY = np.meshgrid(xi, yi)
grid_xy = np.column_stack([XX.ravel(), YY.ravel()])

for ax, buf_m in zip(axes, buffers):
    pts = gdf[gdf.geometry.intersects(poly.buffer(buf_m))]
    px = pts.geometry.x.values; py = pts.geometry.y.values; pz = pts["Bottom1"].values
    
    lin = griddata(np.column_stack([px,py]), pz, grid_xy, method="linear").reshape(elev_m.shape)
    lin_masked = np.where(~np.isnan(elev_m), lin, np.nan)
    n_cells = int((~np.isnan(lin_masked)).sum())
    
    ax.imshow(np.where(~np.isnan(elev_m), elev_m, np.nan),
              origin="lower", extent=[xmin,xmax,ymin,ymax], cmap="Greys", aspect="auto", alpha=0.4)
    ax.imshow(np.where(~np.isnan(lin_masked), lin_masked, np.nan),
              origin="lower", extent=[xmin,xmax,ymin,ymax], cmap="RdYlBu_r", aspect="auto",
              alpha=0.85, vmin=np.nanmin(pz), vmax=np.nanmax(pz))
    from shapely.geometry import box as sbox
    gpd.GeoSeries([poly]).plot(ax=ax, facecolor="none", edgecolor="red", lw=1.5)
    ax.scatter(px, py, s=1, c="k", alpha=0.15)
    ax.set_title(f"Buffer={buf_m} m | pts={len(pts)} | cells={n_cells}")
    ax.set_aspect("equal")
    # Mark mid-east region
    mid_x = (xmin+xmax)/2
    mid_y = (ymin+ymax)/2
    ax.axvline(mid_x, color="cyan", lw=1, ls="--")
    ax.axhline(mid_y, color="cyan", lw=1, ls="--")
    ax.set_xlabel("X (UTM 19S)")
    ax.set_ylabel("Y (UTM 19S)")

plt.suptitle("Penitente — BOT coverage vs buffer size\nCyan lines = basin midpoint", y=1.01)
plt.tight_layout()
plt.savefig("/tmp/bot_buffer_compare.png", dpi=100, bbox_inches="tight")
print("Saved /tmp/bot_buffer_compare.png")
