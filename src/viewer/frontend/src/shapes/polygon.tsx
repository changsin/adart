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

    const keypoints: fabric.Object[] = [];
    for (let i = 0; i < points.length; i++) {
        const currPoint = points[i];

        const circle = new fabric.Circle({
            left: currPoint.x,
            top: currPoint.y,
            radius: 1,
            fill: "black",
        });
        keypoints.push(circle);
    }

    const group = new fabric.Group(keypoints, {
        selectable: true
    });
    
    canvas.add(group);

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

// export const Segmentation: React.FC<ShapeRenderProps> = ({ shape, color = 'black', opacity = 0.3, canvas, onSelectHandler }) => {
//     if (!shape || !shape.points) {
//         // Handle error when shape or points is null/undefined
//         return null;
//     }

//     var rgbaColor = color;
//     // Extract the color attribute from the attributes list
//     const attributes = shape.attributes;
//     if (attributes && Array.isArray(attributes)) {
//         const colorAttribute = attributes.find(attribute => attribute.attribute_name === "color");
//         if (colorAttribute && colorAttribute.attribute_value) {
//             const tmpColor = colorAttribute.attribute_value;
    
//             // Convert RGBA values to rgba CSS color string
//             rgbaColor = `rgba(${tmpColor.r}, ${tmpColor.g}, ${tmpColor.b}, ${tmpColor.a / 255})`;
//         }
//     }

//     const { points, label } = shape
//     const pathCommands = [];
//     const keypoints: fabric.Object[] = [];

//     for (let i = 1; i < points.length; i++) {
//         const prevPoint = points[i - 1];
//         const currPoint = points[i];
    
//         const pathCommand = `L${prevPoint.x},${prevPoint.y} ${currPoint.x},${currPoint.y}`;
//         pathCommands.push(pathCommand);

//         const circle = new fabric.Circle({
//             left: currPoint.x,
//             top: currPoint.y,
//             radius: 0.5,
//             fill: "black",
//         });
//         keypoints.push(circle);
//     }

//     const pathString = `M${points[0].x},${points[0].y} ${pathCommands.join(" ")}`;

//     const path = new fabric.Path(pathString, {
//         stroke: rgbaColor,
//         fill: rgbaColor,
//         strokeWidth: 0.5,
//         opacity,
//     });

//     canvas.add(path);
    
//     const group = new fabric.Group(keypoints, {
//         selectable: true
//     });
    
//     canvas.add(group);

//     return null;
// }

// export const Segmentation: React.FC<ShapeRenderProps> = ({ shape, color = 'black', opacity = 0.3, canvas, onSelectHandler }) => {
//     if (!shape || !shape.points || !canvas || typeof canvas.width !== 'number' || typeof canvas.height !== 'number') {
//         // Handle error when shape, points, or canvas is null/undefined, or canvas dimensions are not numbers
//         return null;
//     }

//     var rgbaColor = null;
//     // Extract the color attribute from the attributes list
//     const attributes = shape.attributes;
//     if (attributes && Array.isArray(attributes)) {
//         const colorAttribute = attributes.find(attribute => attribute.attribute_name === "color");
//         if (colorAttribute && colorAttribute.attribute_value) {
//             rgbaColor = colorAttribute.attribute_value;
//         }
//     }
//     // var rgbaColor = color;
//     // // Extract the color attribute from the attributes list
//     // const attributes = shape.attributes;
//     // if (attributes && Array.isArray(attributes)) {
//     //     const colorAttribute = attributes.find(attribute => attribute.attribute_name === "color");
//     //     if (colorAttribute && colorAttribute.attribute_value) {
//     //         const tmpColor = colorAttribute.attribute_value;
    
//     //         // Convert RGBA values to rgba CSS color string
//     //         rgbaColor = `rgba(${tmpColor.r}, ${tmpColor.g}, ${tmpColor.b}, ${tmpColor.a / 255})`;
//     //     }
//     // }

//     const { points, label } = shape;
//     const imageData = canvas.getContext().getImageData(0, 0, canvas.width, canvas.height);
//     const pixelData = imageData.data;

//     // Create a function to check if a point is inside the polygon
//     const isPointInPolygon = (x: number, y: number) => {
//         let inside = false;
//         for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
//             const xi = points[i].x;
//             const yi = points[i].y;
//             const xj = points[j].x;
//             const yj = points[j].y;

//             const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
//             if (intersect) {
//                 inside = !inside;
//             }
//         }
//         return inside;
//     };

//     // Iterate over the canvas dimensions and fill pixels inside the polygon
//     for (let y = 0; y < canvas.height; y++) {
//         for (let x = 0; x < canvas.width; x++) {
//             const index = (y * canvas.width + x) * 4; // Calculate the index for the current pixel

//             // Check if the pixel is inside the polygon
//             if (isPointInPolygon(x, y)) {
//                 pixelData[index] = rgbaColor.r;
//                 pixelData[index + 1] = rgbaColor.g;
//                 pixelData[index + 2] = rgbaColor.b;
//                 pixelData[index + 3] = rgbaColor.a * 255;
//             }
//         }
//     }

//     // Update the canvas with the modified image data
//     canvas.getContext().putImageData(imageData, 0, 0);

//     return null;
// }
