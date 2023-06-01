import React from "react";
import { fabric } from "fabric"
import { SplinePoint, ShapeRenderProps } from "../interfaces";

const default_line_width = 0.5;

export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.5, canvas, onSelectHandler }) => {
  const { shapeType, points, label } = shape;

  const pathStrings: string[] = [];
  const innerPathStrings: string[] = [];
  const outerPathStrings: string[] = [];

  for (let i = 0; i < points.length; i++) {
    const currPoint = points[i];
    const currWidth = (currPoint as SplinePoint).r;

    const innerControlPoint = new fabric.Point(currPoint.x - currWidth, currPoint.y);
    const outerControlPoint = new fabric.Point(currPoint.x + currWidth, currPoint.y);

    if (i === 0) {
      pathStrings.push(`M${currPoint.x},${currPoint.y}`);
      innerPathStrings.push(`M${innerControlPoint.x},${innerControlPoint.y}`);
      outerPathStrings.push(`M${outerControlPoint.x},${outerControlPoint.y}`);
    } else {
      const prevPoint = points[i - 1];
      const prevWidth = (prevPoint as SplinePoint).r;

      const innerPrevControlPoint = new fabric.Point(prevPoint.x - prevWidth, prevPoint.y);
      const outerPrevControlPoint = new fabric.Point(prevPoint.x + prevWidth, prevPoint.y);

      pathStrings.push(`C${prevPoint.x},${prevPoint.y} ${currPoint.x},${currPoint.y} ${currPoint.x},${currPoint.y}`);
      innerPathStrings.push(`C${innerPrevControlPoint.x},${innerPrevControlPoint.y} ${innerControlPoint.x},${innerControlPoint.y} ${innerControlPoint.x},${innerControlPoint.y}`);
      outerPathStrings.push(`C${outerPrevControlPoint.x},${outerPrevControlPoint.y} ${outerControlPoint.x},${outerControlPoint.y} ${outerControlPoint.x},${outerControlPoint.y}`);
    }
  }

  const pathString = pathStrings.join(" ");
  const innerPathString = innerPathStrings.join(" ");
  const outerPathString = outerPathStrings.join(" ");

  if (shapeType === "boundary" && color !== "red") {
    color = "yellow";
  }

  const path = new fabric.Path(pathString, {
    stroke: color,
    fill: '',
    strokeWidth: default_line_width,
    opacity,
  });

  const innerPath = new fabric.Path(innerPathString, {
    stroke: color,
    fill: '',
    strokeWidth: default_line_width,
    opacity,
  });

  const outerPath = new fabric.Path(outerPathString, {
    stroke: color,
    fill: '',
    strokeWidth: default_line_width,
    opacity,
  });

  const group = new fabric.Group([path, innerPath, outerPath], {
    selectable: true,
    strokeWidth: default_line_width,
  });

  canvas.add(group);

  group.on("mousedown", () => {
    canvas.discardActiveObject();
    group.trigger("selected");
  });

  group.on("mouseup", (event) => {
    if (!event.target) {
      group.trigger("deselected");
    }
  });

  group.on("selected", () => {
    group.strokeWidth = default_line_width * 2;
    if (onSelectHandler) {
      onSelectHandler(shape, group);
    }
  });

  group.on("deselected", () => {
    group.strokeWidth = default_line_width;
  });

  const controlPoints = drawControlPoints(points as SplinePoint[], 'black');
  controlPoints.forEach((point) => {
    canvas.add(point);
  });

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
          strokeWidth: default_line_width,
      });

      controlPoints.push(line_x)
  }

  return controlPoints;
}
