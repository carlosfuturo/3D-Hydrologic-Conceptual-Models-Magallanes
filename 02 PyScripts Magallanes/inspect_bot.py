import geopandas as gpd
import numpy as np

BASE = "/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes"
BASIN_SHP = BASE + "/01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp"
basins = gpd.read_file(BASIN_SHP)
print("Basins:", basins["NOMBRE"].tolist())

for label, bot_shp, basin_name in [
    ("Penitente", BASE + "/03 SIG Magallanes/propsBOT_Vertientes_Proj.shp", "RIO PENITENTE"),
    ("El Oro",    BASE + "/03 SIG Magallanes/propsBOT_Fuego_Proj.shp",     "RIO DEL ORO"),
]:
    gdf = gpd.read_file(bot_shp)
    basin = basins.loc[basins["NOMBRE"] == basin_name, "geometry"].iloc[0]
    clipped = gdf[gdf.geometry.intersects(basin)]
    print(f"=== {label} ===")
    print(f"  CRS: {gdf.crs}")
    print(f"  Geom types: {gdf.geom_type.unique()}")
    print(f"  All cols: {list(gdf.columns)}")
    print(f"  Total features: {len(gdf)} | Intersecting basin: {len(clipped)}")
    if len(clipped):
        print(f"  Bottom1 stats: min={clipped['Bottom1'].min():.1f}, max={clipped['Bottom1'].max():.1f}, mean={clipped['Bottom1'].mean():.1f}")
        print(f"  Sample Bottom1: {clipped['Bottom1'].values[:10]}")
    print()
