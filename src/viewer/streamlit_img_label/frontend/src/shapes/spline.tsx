import React from "react";
import { fabric } from "fabric"
import { SplinePoint, ShapeRenderProps } from "../interfaces";

export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.3, canvas }) => {
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

  if (shapeType === "boundary") {
    color = "yellow"
  }

  const path = new fabric.Path(pathString, {
    stroke: color,
    fill: '',
    strokeWidth: 5,
    opacity,
  });

  console.log(pathString)

  canvas.add(path);

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
