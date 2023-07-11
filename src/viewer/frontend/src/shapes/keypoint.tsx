import React from "react";
import { fabric } from "fabric"
import { ShapeRenderProps, Point } from "../interfaces";
  
export const Keypoint: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.5, canvas, onSelectHandler }) => {
    if (!shape || !shape.points) {
        // Handle error when shape or points is null/undefined
        return null;
    }

    const { points, label } = shape

    const keypoints: fabric.Object[] = [];

    for (let i = 0; i < points.length; i++) {
        const currPoint = points[i];

        const circle = new fabric.Circle({
            left: currPoint.x,
            top: currPoint.y,
            radius: 5,
            fill: color,
        });
        keypoints.push(circle);
    }

    const group = new fabric.Group(keypoints, {
        selectable: true
    });
    
    canvas.add(group);
    
    group.on("mousedown", () => {
        canvas.discardActiveObject(); // Deselect any previously selected object
        group.trigger("selected"); // Manually trigger the selected event
    });
    
    group.on("mouseup", (event) => {
        group.trigger("deselected"); // Manually trigger the deselected event
      });
    
      // Add a click event listener to show the highlight rectangle
      group.on("selected", () => {
        group.strokeWidth = 5;
        if (onSelectHandler) {
          onSelectHandler(shape, group);
        }
      });
    
      // Add a click event listener to hide the highlight rectangle
      group.on("deselected", () => {
        group.strokeWidth = 1;
      });
    
    return null;
}
