import React from "react";
import { fabric } from "fabric"
import { ShapeRenderProps, Point } from "../interfaces";
import { sendSelectedShape } from "../streamlit-utils";
  
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

export const Polygon: React.FC<ShapeRenderProps> = ({ shape, color = 'purple', opacity = 0.3, canvas }) => {
    if (!shape || !shape.points) {
        // Handle error when shape or points is null/undefined
        return null;
    }

    const { points, label } = shape
    const polygon = new fabric.Polygon(points, {
        fill: color,
        stroke: color,
        opacity: opacity,
        strokeWidth: 1,
    });

    const selectedPolygon = new fabric.Polygon(points, {
        fill: color,
        stroke: color,
        opacity: 1,
        strokeWidth: 3,
        visible: false
    });

    canvas.add(polygon);
    canvas.add(selectedPolygon);

    polygon.on("mousedown", () => {
        canvas.discardActiveObject(); // Deselect any previously selected object
        if (selectedPolygon.visible) {
            // If the annotation is already selected, deselect it
            polygon.trigger("deselected"); // Manually trigger the deselected event
            selectedPolygon.visible = false;
        } else {
            // Otherwise, select the annotation
            selectedPolygon.set({visible: true});
            canvas.setActiveObject(selectedPolygon);
            polygon.trigger("selected"); // Manually trigger the selected event
        }
    });
    
    polygon.on("mouseup", (event) => {
          if (!event.target) {
          // If no object is clicked, deselect any selected object
          const activeObject = canvas.getActiveObject();
          if (activeObject === selectedPolygon) {
            polygon.trigger("deselected"); // Manually trigger the deselected event
            selectedPolygon.visible = false;
          }
          }
      });
    
      // Add a click event listener to show the highlight rectangle
      polygon.on("selected", () => {
        selectedPolygon.set({visible: true});
          canvas.setActiveObject(selectedPolygon);
    
          console.log("selected " + shape)
          sendSelectedShape(shape)
      });
    
      // Add a click event listener to hide the highlight rectangle
      polygon.on("deselected", () => {
        selectedPolygon.visible = false;
      });
    
    return null;
}
