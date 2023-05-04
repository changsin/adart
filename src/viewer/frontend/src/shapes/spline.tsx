import React from "react";
import { fabric } from "fabric"
import { SplinePoint, ShapeRenderProps } from "../interfaces";

export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.3, canvas, onSelectHandler }) => {
  const { shapeType, points, label } = shape;

  let pathString = '';
  const firstPoint = new fabric.Point(points[0].x, points[0].y);

  pathString += `M${firstPoint.x},${firstPoint.y}`;

  for (let i = 1; i < points.length; i++) {
    const prevPoint = points[i - 1];
    const currPoint = points[i];
    const strokeWidth = (prevPoint as SplinePoint).r;

    pathString += `L${currPoint.x},${currPoint.y}`;
  }
// export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.3, canvas }) => {
//   const { shapeType, points, label } = shape;

//   let pathString = '';
//   const firstPoint = new fabric.Point(points[0].x, points[0].y);
//   let strokeWidth = (points[0] as SplinePoint).r;

//   pathString += `M${firstPoint.x},${firstPoint.y}`;

//   for (let i = 1; i < points.length - 2; i++) {
//     const prevPoint = points[i - 1];
//     const currPoint = points[i];
//     const nextPoint = points[i + 1];
//     const endStrokeWidth = (nextPoint as SplinePoint).r;

//     const cp1 = new fabric.Point(currPoint.x - (nextPoint.x - prevPoint.x) / 6, currPoint.y - (nextPoint.y - prevPoint.y) / 6);
//     const cp2 = new fabric.Point(nextPoint.x + (currPoint.x - nextPoint.x) / 6, nextPoint.y + (currPoint.y - nextPoint.y) / 6);

//     pathString += `C${cp1.x},${cp1.y},${cp2.x},${cp2.y},${nextPoint.x},${nextPoint.y}`;
//     strokeWidth = endStrokeWidth;
//   }

//   const lastPoint = new fabric.Point(points[points.length - 1].x, points[points.length - 1].y);
//   pathString += `L${lastPoint.x},${lastPoint.y}`;

//   const spline = new fabric.Path(pathString, {
//     stroke: color,
//     strokeWidth: strokeWidth,
//     fill: '',
//     opacity: opacity,
//     selectable: false
//   });

//   canvas.add(spline);
// export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.2, canvas }) => {
//   const { shapeType, points, label } = shape;

//   let pathString = '';
//   const firstPoint = new fabric.Point(points[0].x, points[0].y);
//   const strokeWidth = (points[0] as SplinePoint).r;

//   pathString += `M${firstPoint.x},${firstPoint.y}`;

//   for (let i = 1; i < points.length - 2; i++) {
//     const prevPoint = points[i - 1];
//     const currPoint = points[i];
//     const nextPoint = points[i + 1];
//     const endStrokeWidth = (nextPoint as SplinePoint).r;

//     const cp1 = new fabric.Point(currPoint.x - (nextPoint.x - prevPoint.x) / 6, currPoint.y - (nextPoint.y - prevPoint.y) / 6);
//     const cp2 = new fabric.Point(nextPoint.x + (currPoint.x - nextPoint.x) / 6, nextPoint.y + (currPoint.y - nextPoint.y) / 6);

//     const distance = Math.abs(nextPoint.x - currPoint.x);
//     const strokeWidth = Math.max(1, (endStrokeWidth * (distance / 100)));

//     pathString += `C${cp1.x},${cp1.y},${cp2.x},${cp2.y},${nextPoint.x},${nextPoint.y}`;
    
//     const spline = new fabric.Path(pathString, {
//       stroke: color,
//       strokeWidth: strokeWidth,
//       fill: '',
//       opacity: opacity,
//       selectable: false
//     });
  
//     canvas.add(spline);
  // }

  // const lastPoint = new fabric.Point(points[points.length - 1].x, points[points.length - 1].y);
  // pathString += `L${lastPoint.x},${lastPoint.y}`;

  // const spline = new fabric.Path(pathString, {
  //   stroke: color,
  //   strokeWidth: strokeWidth,
  //   fill: '',
  //   opacity: opacity,
  //   selectable: false
  // });

  // canvas.add(spline);

  if (shapeType === "boundary" && color != "red") {
    color = "yellow"
  }

  const path = new fabric.Path(pathString, {
    stroke: color,
    fill: '',
    strokeWidth: 5,
    opacity,
  });

  const selectedPath = new fabric.Path(pathString, {
    stroke: color,
    fill: '',
    strokeWidth: 10,
    opacity,
    visible: false
  });

  canvas.add(path);
  canvas.add(selectedPath);

  path.on("mousedown", () => {
    canvas.discardActiveObject(); // Deselect any previously selected object
    if (selectedPath.visible) {
        // If the annotation is already selected, deselect it
        path.trigger("deselected"); // Manually trigger the deselected event
        selectedPath.visible = false;
    } else {
        // Otherwise, select the annotation
        selectedPath.set({visible: true});
        canvas.setActiveObject(selectedPath);
        path.trigger("selected"); // Manually trigger the selected event
    }
  });

  path.on("mouseup", (event) => {
      if (!event.target) {
      // If no object is clicked, deselect any selected object
      const activeObject = canvas.getActiveObject();
      if (activeObject === selectedPath) {
          path.trigger("deselected"); // Manually trigger the deselected event
          selectedPath.visible = false;
      }
    }
  });

  // // Add a click event listener to show the highlight rectangle
  path.on("selected", () => {
    selectedPath.set({visible: true});
    canvas.setActiveObject(selectedPath);

    if (onSelectHandler) {
      onSelectHandler(shape, path);
    }
  });

  // Add a click event listener to hide the highlight rectangle
  path.on("deselected", () => {
      selectedPath.visible = false;
  });

  const controlPoints = drawControlPoints(points as SplinePoint[], 'black')
  controlPoints.forEach(((point) => {
      canvas.add(point)
  }))

  return null;
};

function drawControlPoints(points: SplinePoint[], color: string = 'black'): fabric.Object[] {
    const controlPoints: fabric.Object[] = [];

  for (let i = 0; i < points.length; i++) {
      const x = points[i].x
      const y = points[i].y
      const x_offset = points[i].r;
      const line_x = new fabric.Line([x - x_offset, y, x + x_offset, y], {
          stroke: color,
          strokeWidth: 1,
      });

      controlPoints.push(line_x)
  }

  return controlPoints;
}
