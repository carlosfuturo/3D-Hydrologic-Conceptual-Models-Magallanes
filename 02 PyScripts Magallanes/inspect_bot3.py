import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.spatial import ConvexHull

BASE = "/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes"
BASIN_SHP = BASE + "/01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp"
BOT_SHP   = BASE + "/03 SIG Magallanes/propsBOT_Vertientes_Proj.shp"

basins = gpd.read_file(BASIN_SHP)
poly = basins.loc[basins["NOMBRE"] == "RIO PENITENTE", "geometry"].iloc[0]
xmin, ymin, xmax, ymax = poly.bounds

gdf  = gpd.read_file(BOT_SHP)
pts  = gdf[gdf.geometry.intersects(poly)].copy()
px   = pts.geometry.x.values
py   = pts.geometry.y.values
pz   = pts["Bottom1"].values.astype(float)

# build test grid same as script (80 cells)
N   = 80
xi  = np.linspace(xmin, xmax, N)
yi  = np.linspace(ymin, ymax, N)
XX, YY = np.meshgrid(xi, yi)
gxy = np.column_stack([XX.ravel(), YY.ravel()])

lin = griddata(np.column_stack([px,py]), pz, gxy, method="linear").reshape(N,N)
nn  = griddata(np.column_stack([px,py]), pz, gxy, method="nearest").reshape(N,N)

# convex hull mask  
hull = ConvexHull(np.column_stack([px, py]))
from matplotlib.path import Path
hull_path = Path(np.column_stack([px, py])[hull.vertices])
in_hull   = hull_path.contains_points(gxy).reshape(N, N)

# fill within hull using nearest; strict linear outside hull stays NaN
filled = np.where(np.isnan(lin) & in_hull, nn, lin)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for ax, z, title in [
    (axes[0], lin,    "linear only"),
    (axes[1], filled, "linear + NN within hull"),
    (axes[2], in_hull.astype(float), "convex hull mask"),
]:
    img = ax.imshow(z, origin="lower", extent=[xmin,xmax,ymin,ymax],
                    cmap="RdYlBu_r", aspect="auto")
    gpd.GeoSeries([poly]).plot(ax=ax, facecolor="none", edgecolor="red", lw=1.5)
    ax.scatter(px, py, s=1, c="k", alpha=0.3)
    ax.set_title(f"{title}\ncells with data: {(~np.isnan(z)).sum() if z.dtype!=bool else z.sum()}")
    plt.colorbar(img, ax=ax)
plt.tight_layout()
plt.savefig("/tmp/bot_hull_fill.png", dpi=120)
print("Saved /tmp/bot_hull_fill.png")
print(f"Linear cells: {(~np.isnan(lin)).sum()}")
print(f"Filled (hull) cells: {(~np.isnan(filled)).sum()}")
