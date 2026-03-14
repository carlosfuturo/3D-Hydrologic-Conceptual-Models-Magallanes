import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box

BASE = "/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes"
BASIN_SHP = BASE + "/01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp"
BOT_SHP   = BASE + "/03 SIG Magallanes/propsBOT_Vertientes_Proj.shp"

basins = gpd.read_file(BASIN_SHP)
poly = basins.loc[basins["NOMBRE"] == "RIO PENITENTE", "geometry"].iloc[0]

gdf = gpd.read_file(BOT_SHP)

# Strict intersection (current behaviour)
strict = gdf[gdf.geometry.intersects(poly)]
print(f"Strict intersection: {len(strict)} points")
print(f"  X range: {strict.geometry.x.min():.0f} – {strict.geometry.x.max():.0f}")
print(f"  Y range: {strict.geometry.y.min():.0f} – {strict.geometry.y.max():.0f}")

# Estimate grid spacing from raw data
xs = np.sort(gdf.geometry.x.unique())
spacing = np.median(np.diff(xs))
print(f"\nEstimated grid spacing: {spacing:.0f} m")

# Buffered intersection
buf = poly.buffer(spacing * 1.5)
buffered = gdf[gdf.geometry.intersects(buf)]
print(f"\nBuffered ({spacing*1.5:.0f} m) intersection: {len(buffered)} points")
print(f"  X range: {buffered.geometry.x.min():.0f} – {buffered.geometry.x.max():.0f}")
print(f"  Y range: {buffered.geometry.y.min():.0f} – {buffered.geometry.y.max():.0f}")

# Basin bbox
xmin, ymin, xmax, ymax = poly.bounds
print(f"\nBasin bounds: X {xmin:.0f}–{xmax:.0f} | Y {ymin:.0f}–{ymax:.0f}")
print(f"Basin mid-east X > {(xmin+xmax)/2:.0f}")

# How many strict points are in east half?
east_strict = strict[strict.geometry.x > (xmin+xmax)/2]
east_buffered = buffered[buffered.geometry.x > (xmin+xmax)/2]
print(f"\nStrict points in east half: {len(east_strict)}")
print(f"Buffered points in east half: {len(east_buffered)}")

# Quick map
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
for ax, pts, label in [(axes[0], strict, "Strict"), (axes[1], buffered, "Buffered")]:
    gpd.GeoSeries([poly]).plot(ax=ax, facecolor="none", edgecolor="red", linewidth=1.5)
    if len(pts):
        ax.scatter(pts.geometry.x, pts.geometry.y, c=pts["Bottom1"], s=3, cmap="RdYlBu", vmin=pts["Bottom1"].min(), vmax=pts["Bottom1"].max())
    ax.set_title(f"{label}: {len(pts)} pts")
    ax.set_aspect("equal")
plt.tight_layout()
plt.savefig("/tmp/bot_penitente_coverage.png", dpi=120)
print("\nMap saved to /tmp/bot_penitente_coverage.png")
