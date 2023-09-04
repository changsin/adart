import React from "react";
import { fabric } from "fabric"
import { ShapeRenderProps, Point } from "../interfaces";
  
export const VanishingPoint: React.FC<ShapeRenderProps> = ({ shape, color = 'red', opacity = 0.5, canvas }) => {
    if (!shape || !shape.points) {
        // Handle error when shape or points is null/undefined
        return null;
    }

    const { points, label } = shape

    const { x, y } = points[0] as Point

    const x_offset = 40
    const y_offset = 20
    const line_x = new fabric.Line([x - x_offset, y, x + x_offset, y], {
        stroke: color,
        strokeWidth: 1,
        opacity: opacity
    });
    const line_y = new fabric.Line([x, y - y_offset, x, y + y_offset], {
        stroke: color,
        strokeWidth: 1,
        opacity: opacity
    });

    canvas.add(line_x);
    canvas.add(line_y);

    return null;
}

export const Polygon: React.FC<ShapeRenderProps> = ({ shape, color = 'purple', opacity = 0.3, canvas, onSelectHandler }) => {
    if (!shape || !shape.points) {
        // Handle error when shape or points is null/undefined
        return null;
    }

    var rgbaColor = color;
    // Extract the color attribute from the attributes list
    const attributes = shape.attributes;
    if (attributes && Array.isArray(attributes)) {
        const colorAttribute = attributes.find(attribute => attribute.attribute_name === "color");
        if (colorAttribute && colorAttribute.attribute_value) {
            const color = colorAttribute.attribute_value;
    
            // Convert RGBA values to rgba CSS color string
            rgbaColor = `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a / 255})`;
        }
    }

    const { points, label } = shape
    const polygon = new fabric.Polygon(points, {
        fill: rgbaColor,
        stroke: rgbaColor,
        opacity: opacity,
        strokeWidth: 1,
    });

    canvas.add(polygon);

    polygon.on("mousedown", () => {
        canvas.discardActiveObject(); // Deselect any previously selected object
        polygon.trigger("selected"); // Manually trigger the selected event
    });
    
    polygon.on("mouseup", (event) => {
        polygon.trigger("deselected"); // Manually trigger the deselected event
      });
    
      // Add a click event listener to show the highlight rectangle
      polygon.on("selected", () => {
        polygon.strokeWidth = 5;
        if (onSelectHandler) {
          onSelectHandler(shape, polygon);
        }
      });
    
      // Add a click event listener to hide the highlight rectangle
      polygon.on("deselected", () => {
        polygon.strokeWidth = 1;
      });
    
    return null;
}
