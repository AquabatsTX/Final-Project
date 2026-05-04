# FINAL
# Python-Based Spatial Analysis for Groundwater Risk Classification and Stream Proximity

**Course:** GEO 5419 Advanced GIS  
**Group:** Aquabats - Eric Boronow, Swathi Dasari, Adrian Urrutia, Genesis Sanchez  
**Toolbox:** `Edwards_Aquifer_Risk_Test.atbx`  
**Script:** `EdwardsAquiferVulnerabilityTool.py`

## Project summary

This ArcGIS Pro script tool converts a tabular dataset with X/Y or latitude/longitude coordinate fields into spatial point features, classifies each point by Edwards Aquifer zone, checks whether each point falls within Hays County, and calculates the distance from each point to the nearest Hays County stream. The tool is intended as a screening-level GIS decision-support workflow for evaluating groundwater vulnerability and hydrologic context for point-based environmental, regulatory, or planning datasets in Hays County, Texas.

## Main workflow

1. Convert the input table into a point feature class using user-selected coordinate fields.
2. Spatially join points to the Hays County boundary and assign an `In_Hays` value.
3. Project points and streams to Texas State Plane Central, NAD 1983, Feet (`EPSG:2278`) for distance analysis.
4. Classify points by Edwards Aquifer zone:
   - Recharge Zone: High
   - Transition Zone: Moderate
   - Contributing Zone: Moderate
   - Contributing Zone within the Transition Zone: Low-Moderate
   - Outside Edwards Aquifer: Outside
5. Generate a nearest-stream table and join stream name and distance values back to the point features.
6. Convert stream distance from feet to miles.
7. Save the final output feature class to the user-selected workspace.

## Required tool inputs

| Parameter | Description |
| Input Excel Table | Table containing point locations and coordinate fields. Excel, CSV, or other ArcGIS-readable tables may be used. |
| X Coordinate Field | Field containing X coordinates or longitude values. |
| Y Coordinate Field | Field containing Y coordinates or latitude values. |
| Input Coordinate System | Spatial reference of the input coordinate fields. |
| Edwards Recharge Zone | Feature layer for the Edwards Aquifer Recharge Zone. |
| Edwards Transition Zone | Feature layer for the Edwards Aquifer Transition Zone. |
| Edwards Contributing Zone | Feature layer for the Edwards Aquifer Contributing Zone. |
| Edwards Contributing-Within-Transition Zone | Feature layer for the Contributing Zone within the Transition Zone. |
| Hays County Streams | Stream, creek, or river feature layer used for nearest-stream distance calculations. |
| Hays County Boundary | County boundary feature layer used to identify whether points are inside Hays County. |
| Output Workspace | Folder or geodatabase where the final output feature class will be saved. |
| Output Feature Class Name | Base name for the output feature class. The script appends `_StatePlane` to the final output name. |

## Output fields

The output feature class includes the original table attributes plus added GIS classification fields:

| Field | Description |
| `In_Hays` | Indicates whether each point intersects the Hays County boundary. |
| `AquiferZone` | Edwards Aquifer zone classification assigned by spatial intersection. |
| `Risk_Class` | Relative groundwater vulnerability class based on aquifer zone. |
| `NAME` | Name of the nearest stream feature, when available in the stream dataset. |
| `NEAR_DIST` | Distance to the nearest stream in feet. |
| `Dist_Stream_mi` | Distance to the nearest stream in miles. |

## Sample data notes

Sample data stored in the repository's `data` folder. This project uses real-world spatial and tabular data, including:

- Edwards Aquifer zone layers from the Edwards Aquifer Authority.
- Hays County boundary data from the Hays County GIS open data portal.
- Hays County stream data from the Hays County GIS open data portal.
- TCEQ tabular water activity records, such as Notices of Violation or Notices of Enforcement, for demonstration purposes.

Users should confirm that tabular input data contains valid coordinate fields before running the tool. Address-only datasets must be geocoded before use.

## How to run the tool in ArcGIS Pro

1. Open the ArcGIS Pro project.
2. Add or connect to the `Edwards_Aquifer_Risk_Test.atbx` toolbox.
3. Open the script tool from the toolbox.
4. Select the input table and coordinate fields.
5. Set the input coordinate system.
6. Select the Edwards Aquifer zone layers, Hays County streams, and Hays County boundary layer.
7. Choose an output workspace and output feature class name.
8. Run the tool.
9. Review the tool messages and inspect the output feature class in the map and attribute table.

## Limitations

This tool requires tabular input data with usable coordinate fields. It does not geocode street addresses, model groundwater flow paths, estimate contaminant transport, or account for pollutant volume, duration, or severity. Stream proximity is used as a screening-level indicator of hydrologic context, not as a replacement for detailed hydrogeologic modeling.

## Repository structure

Aquabats_FinalProject/
|-- Edwards_Aquifer_Risk_Test.atbx
|-- TestCodeFinal.py
|-- README.md
|-- Aquabats_FinalReport_202605_touched_up.docx
|-- data/
|   |-- sample input table(s)
|   |-- Edwards Aquifer zone layers
|   |-- Hays County boundary layer
|   |-- Hays County streams layer
|-- docs/
|   |-- optional workflow figures, screenshots, or tool documentation notes
