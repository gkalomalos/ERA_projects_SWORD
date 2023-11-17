import json
from pathlib import Path
import sys
from time import time

from climada.entity import Exposures
import geopandas as gpd

from constants import (
    DATA_EXPOSURES_DIR,
    DATA_DIR,
    TEMP_DIR
)


def update_progress(progress, message):
    progress_data = {"type": "progress", "progress": progress, "message": message}
    print(json.dumps(progress_data))
    # print("\033[93m" + f"send progress {progress} to frontend." + "\033[0m")
    sys.stdout.flush()


def run_test(request: dict) -> dict:
    print("here")
    initial_time = time()
    update_progress(10, "Initiating...")
    filepath = Path(DATA_DIR) / "dev" / "gadm41_EGY.gpkg"
    layer = 2
    update_progress(30, "Read Exposure data")
    exposure_filepath = Path(DATA_EXPOSURES_DIR) / "LitPop_150arcsec_EGY.hdf5"
    exposure = Exposures().from_hdf5(exposure_filepath)
    exp_gdf = exposure.gdf
    update_progress(50, "Read Administrative data")
    adm_gdf = gpd.read_file(
        filepath, layer=layer
    )  # access layers by index (ex: 1) or name (ex: 'ADM_ADM_0')
    joined_gdf = gpd.sjoin(exp_gdf, adm_gdf, how="left", predicate="within")
    aggregated_values = joined_gdf.groupby(f"GID_{layer}")["value"].sum().reset_index()
    adm_gdf = adm_gdf.merge(aggregated_values, on=f"GID_{layer}", how="left")
    update_progress(70, "Join data")
    adm_gdf["value"] = adm_gdf["value"].fillna(0)
    resp_gdf = adm_gdf[["NAME_1", "geometry", "value"]]
    map_data = resp_gdf.to_json()
    exposure_data_filepath = Path(TEMP_DIR) / "output.geojson"

    with open(exposure_data_filepath, "w") as file:
        file.write(map_data)

    update_progress(90, "Finish process")
    response = {
        "data": {"mapTitle": "Test Egypt map", "mapData": str(exposure_data_filepath)},
        "status": {
            "code": 2000,
            "message": f"Exposure set successfully in {time() - initial_time}sec.",
        },
    }
    return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    response = run_test(request)
    print(json.dumps(response))
