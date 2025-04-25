from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsSymbol,
)
from PyQt5.QtGui import QColor
import os

# Define the folder where the GeoJSON files are stored
input_folder = "Transmissions"  # Replace with your folder path if not in the current directory
output_project = "Prova per transmissions.qgz"  # Output QGIS project file

# Initialize QGIS Project instance
project = QgsProject.instance()
def apply_symbology(layer):
    # Ensure the layer has the required fields
    if not layer.fields().indexFromName("color") >= 0 or not layer.fields().indexFromName("Dimension") >= 0:
        print(f"Layer {layer.name()} is missing 'color' or 'Dimension' fields. Skipping styling.")
        return

    # Create a categorized renderer based on the 'color' field
    categories = []
    color_field_idx = layer.fields().indexFromName("color")
    dimension_field_idx = layer.fields().indexFromName("Dimension")

    for feature in layer.getFeatures():
        color = feature[color_field_idx]  # Get the color value
        width = feature[dimension_field_idx]  # Get the dimension (stroke width)

        # Create a symbol for the feature
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(QColor(color))  # Set color from the 'color' field
        symbol.setWidth(float(width))  # Set width from the 'Dimension' field

        # Append to categories
        label = f"Color: {color}, Width: {width}"
        categories.append(QgsRendererCategory(color, symbol, label))

    # Apply the categorized renderer
    renderer = QgsCategorizedSymbolRenderer("color", categories)
    layer.setRenderer(renderer)

    # Refresh the layer to apply symbology
    layer.triggerRepaint()
    print(f"Symbology applied to layer: {layer.name()}")
    
    # Loop through all GeoJSON files in the folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".geojson"):
        file_path = os.path.join(input_folder, file_name)

        # Load the GeoJSON file
        layer = QgsVectorLayer(file_path, file_name, "ogr")
        if not layer.isValid():
            print(f"Failed to load: {file_name}")
            continue

        # Apply symbology to the layer
        apply_symbology(layer)

        # Add the layer to the QGIS project
        project.addMapLayer(layer)
        print(f"Added layer: {file_name}")

# Save the QGIS project
project.write(output_project)
print(f"Project saved to: {output_project}")