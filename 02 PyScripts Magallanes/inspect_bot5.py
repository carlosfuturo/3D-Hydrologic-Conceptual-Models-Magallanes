import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from scipy.ndimage import zoom as nzoom
from scipy.interpolate import griddata

BASE = "/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes"
BASIN_SHP = BASE + "/01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp"
BOT_SHP   = BASE + "/03 SIG Magallanes/propsBOT_Vertientes_Proj.shp"
DEM_PATH  = BASE + "/02 PyScripts Magallanes/DEM_Copernicus_30m/mosaicos/DEM_Cop30_Penitente_UTM19S.tif"

basins = gpd.read_file(BASIN_SHP)
poly   = basins.loc[basins["NOMBRE"] == "RIO PENITENTE", "geometry"].iloc[0]
xmin, ymin, xmax, ymax = poly.bounds

gdf = gpd.read_file(BOT_SHP)

with rasterio.open(DEM_PATH) as src:
    raw, _ = rio_mask(src, [poly], crop=True, nodata=-9999)
    elev_raw = np.flipud(raw[0].astype("float32"))
    elev_raw[elev_raw == -9999] = np.nan
rows, cols = elev_raw.shape
N = 80
zoom_r = N / max(rows, cols)
elev_m = nzoom(elev_raw, zoom_r, order=1, prefilter=False)
nan_w  = nzoom(np.where(np.isnan(elev_raw), 0.0, 1.0).astype("float32"), zoom_r, order=0)
elev_m[nan_w < 0.5] = np.nan

xi = np.linspace(xmin, xmax, elev_m.shape[1])
yi = np.linspace(ymin, ymax, elev_m.shape[0])
XX, YY = np.meshgrid(xi, yi)
mid_x = (xmin + xmax) / 2
mid_y = (ymin + ymax) / 2
grid_xy = np.column_stack([XX.ravel(), YY.ravel()])

print(f"Basin midpoint: X={mid_x:.0f}  Y={mid_y:.0f}")
print(f"DEM shape: {elev_m.shape}")
print()

for buf in [0, 300, 600, 1200, 2400]:
    pts = gdf[gdf.geometry.intersects(poly.buffer(buf))]
    px = pts.geometry.x.values
    py = pts.geometry.y.values
    pz = pts["Bottom1"].values.astype(float)
    lin = griddata(np.column_stack([px, py]), pz, grid_xy, method="linear").reshape(elev_m.shape)
    masked = np.where(~np.isnan(elev_m), lin, np.nan)
    n_total = int((~np.isnan(masked)).sum())
    in_meast = (~np.isnan(masked)) & (XX > mid_x) & (YY > mid_y - (mid_y - ymin) * 0.5) & (YY < mid_y + (ymax - mid_y) * 0.5)
    print(f"buf={buf:5d}m | pts={len(pts):5d} | total_cells={n_total:4d} | mid-east_cells={in_meast.sum():4d}")
