# import ArcGIS Python library and OS module
import arcpy
import os

arcpy.env.overwriteOutput = True

# PARAMETERS

# Read what user chooses when the tool runs in ArcGIS
input_table = arcpy.GetParameterAsText(0)
x_field = arcpy.GetParameterAsText(1)
y_field = arcpy.GetParameterAsText(2)
input_sr = arcpy.GetParameter(3)

#GIS supplied by user
recharge_fc = arcpy.GetParameterAsText(4)
transition_fc = arcpy.GetParameterAsText(5)
contributing_fc = arcpy.GetParameterAsText(6)
contributing_trans_fc = arcpy.GetParameterAsText(7)
streams_fc = arcpy.GetParameterAsText(8)
hays_fc = arcpy.GetParameterAsText(9)

#Where output will be saved and base name for output
out_workspace = arcpy.GetParameterAsText(10)
out_name = arcpy.GetParameterAsText(11)

stateplane_sr = arcpy.SpatialReference(2278)

# CONVERT EXCEL TO POINTS

#Temporary in-memory feature class
#Converts table X/Y coords to point feature class
points_fc = os.path.join("in_memory", "input_points")
arcpy.management.XYTableToPoint(input_table, points_fc, x_field, y_field, coordinate_system = input_sr)

# IDENTIFY HAYS COUNTY POINTS

#Check if points are within Hays County
hays_points = os.path.join("in_memory", "hays_points")
arcpy.analysis.SpatialJoin(points_fc, hays_fc, hays_points, join_type = "KEEP_ALL", match_option = "INTERSECT")
arcpy.management.AddField(hays_points, "In_Hays", "TEXT", 5)
with arcpy.da.UpdateCursor(hays_points, ["Join_Count", "In_Hays"]) as cur:
    for jc, ih in cur:
        ih = "Yes" if jc > 0 else "No"      #Point intersects county or not
        cur.updateRow((jc, ih))

# PROJECT DATA FOR DISTANCE ANALYSIS

# Temporary projected datasets
proj_points = os.path.join("in_memory", "proj_points")
proj_streams = os.path.join("in_memory", "proj_streams")

# reprojects data to StatePlane
arcpy.management.Project(hays_points, proj_points, stateplane_sr)
arcpy.management.Project(streams_fc, proj_streams, stateplane_sr)

# EDWARDS AQUIFER ZONE CLASSIFICATION

#temporary output
aquifer_join_fc = os.path.join("in_memory", "aquifer_join")

arcpy.management.CopyFeatures(proj_points, aquifer_join_fc)

#Determine what points fall within Edwards Aquifer polygons
arcpy.management.AddField(aquifer_join_fc, "AquiferZone", "TEXT", 80)
arcpy.management.AddField(aquifer_join_fc, "Risk_Class", "TEXT", 30)

arcpy.management.MakeFeatureLayer(aquifer_join_fc, "points_lyr")

zone_layers = [(recharge_fc, "Edwards Aquifer Recharge Zone", "High"), (transition_fc, "Edwards Aquifer Transition Zone", "Moderate"),
               (contributing_fc, "Edwards Aquifer Contributing Zone", "Moderate"),
               (contributing_trans_fc, "Edwards Aquifer Contributing Zone within the Transition Zone", "Low-Moderate")]
for zone_fc, zone_name, risk in zone_layers:
    arcpy.management.MakeFeatureLayer(zone_fc, "zone_lyr")
    arcpy.management.SelectLayerByLocation("points_lyr", "INTERSECT", "zone_lyr", selection_type = "NEW_SELECTION")
    with arcpy.da.UpdateCursor("points_lyr", ["AquiferZone", "Risk_Class"]) as cursor:
        for row in cursor:
            row[0] = zone_name
            row[1] = risk
            cursor.updateRow(row)
    arcpy.management.Delete("zone_lyr")

# Default remaining points to Outside
with arcpy.da.UpdateCursor(aquifer_join_fc, ["AquiferZone", "Risk_Class"]) as cursor:
    for row in cursor:
        if row[0] is None:
            row[0] = "Not in Edwards Aquifer"
            row[1] = "Outside"
            cursor.updateRow(row)

#STREAM PROXIMITY ANALYSIS

#temporary near table
near_tbl = os.path.join("in_memory", "near_tbl")

#Generate table that finds nearest stream to each point and calculates distance
arcpy.analysis.GenerateNearTable(aquifer_join_fc, proj_streams, near_tbl, closest = "TRUE", method = "PLANAR")

#Joins distance values to points, adds stream name, and stores distance
arcpy.management.JoinField(aquifer_join_fc, "OBJECTID", near_tbl, "IN_FID", ["NEAR_DIST", "NEAR_FID"])
arcpy.management.JoinField(aquifer_join_fc, "NEAR_FID", proj_streams, "OBJECTID", ["NAME"])
arcpy.management.AddField(aquifer_join_fc, "Dist_Stream_mi", "DOUBLE")

#Loop through each point, convert, convert stream from feet to miles, and store values in output table
with arcpy.da.UpdateCursor(aquifer_join_fc, ["NEAR_DIST", "Dist_Stream_mi"]) as cursor:
    for dist_ft, dist_mi in cursor:
        if dist_ft is not None:
            dist_mi = dist_ft * 0.000189394  # feet to miles
        else:
            dist_mi = None
        cursor.updateRow((dist_ft, dist_mi))

arcpy.AddMessage("Nearest stream name and distance calculated.")

#FINAL OUTPUT

final_output_stateplane = os.path.join(out_workspace, out_name + "_StatePlane")

arcpy.management.CopyFeatures(aquifer_join_fc, final_output_stateplane)

arcpy.AddMessage("Nearest stream name and distance calculated.")
arcpy.AddMessage("Tool completed successfully.")
arcpy.AddMessage("Output saved to: " + final_output_stateplane)
