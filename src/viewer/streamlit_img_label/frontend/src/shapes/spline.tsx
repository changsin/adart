import React from "react";
import { fabric } from "fabric"
import { SplinePoint, ShapeRenderProps } from "../interfaces";

export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.3, canvas }) => {
  const { points, label } = shape;

  // If there are less than two points, return null
  if (points.length < 2) {
    return null;
  }

  // Create an empty path string
  let path = '';
  let default_width = 5;

  const segments: fabric.Object[] = [];

  // Move to the first point
  path += `M ${points[0].x} ${points[0].y}`;

  // Create a spline through all the points
  if (points.length === 2) {
    // If there are only two points, create a straight line
    path += ` L ${points[1].x} ${points[1].y}`;
    const segment = new fabric.Path(path, {
      fill: '',
      stroke: color,
      opacity: opacity,
      strokeWidth: (points[1] as SplinePoint).r || default_width,
    });
    segments.push(segment);
  } else {
    // Otherwise, create a Bezier spline with the control points at each end
    for (let i = 1; i < points.length - 2; i++) {
      const xc = (points[i].x + points[i + 1].x) / 2;
      const yc = (points[i].y + points[i + 1].y) / 2;
      const r = (points[i] as SplinePoint).r;
      const segmentPath = `M ${points[i].x} ${points[i].y} Q ${points[i].x} ${points[i].y}, ${xc} ${yc} T ${points[i + 1].x} ${points[i + 1].y}`;
      const segment = new fabric.Path(segmentPath, {
        fill: '',
        stroke: color,
        opacity: opacity,
        strokeWidth: r || default_width,
      });
      segments.push(segment);
    }
    // Add the last point to the path
    path += ` Q ${points[points.length - 2].x} ${points[points.length - 2].y}, ${points[points.length - 1].x} ${points[points.length - 1].y}`;
    const lastSegment = new fabric.Path(path, {
      fill: '',
      stroke: color,
      strokeWidth: (points[points.length - 1] as SplinePoint).r || default_width,
    });
    segments.push(lastSegment);
  }
  console.log(path)

  // Create a Fabric.js path object from the path string
  const group = new fabric.Group(segments, {
    selectable: true,
  });

  // If the spline is an instance of fabric.Object, add it to the canvas
  if (group && group instanceof fabric.Object) {
      canvas.add(group);
  }

  const controlPoints = drawControlPoints(points as SplinePoint[], color)
  controlPoints.forEach(((point) => {
      canvas.add(point)
  }))

  return null;
}

  function drawControlPoints(points: SplinePoint[], color: string): fabric.Object[] {
    const controlPoints: fabric.Object[] = [];

  for (let i = 0; i < points.length; i++) {
      const x = points[i].x
      const y = points[i].y
      const x_offset = points[i].r / 2;
      const line_x = new fabric.Line([x - x_offset, y, x + x_offset, y], {
          stroke: color,
          strokeWidth: 1,
      });

      controlPoints.push(line_x)
  }

  return controlPoints;
}
