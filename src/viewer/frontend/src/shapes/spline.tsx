import React from "react";
import { fabric } from "fabric"
import { SplinePoint, ShapeRenderProps, Occlusion } from "../interfaces";

const default_line_width = 0.5;

export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.5, canvas, onSelectHandler }) => {
  const { shapeType, points, attributes } = shape;

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

  // Fill the area between inner and outerPath with areaPath
  const reversedOuterPathString = outerPathString
  .split(" ")
  .reverse()
  .map((command) => {
    if (command.startsWith("M")) {
      // Change M command to L command because M will start a new path
      return command.replace("M", "L");
    }
    return command;
  })
  .join(" ");

  const areaPathString = `${innerPathString} L${points[points.length - 1].x},${points[points.length - 1].y} ${reversedOuterPathString} Z`;

  const areaPath = new fabric.Path(areaPathString, {
    stroke: '',
    fill: color,
    opacity,
  });

  const group = new fabric.Group([path, innerPath, outerPath, areaPath], {
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

  if (attributes && attributes?.occlusions) {
    const occlusions: Occlusion[] = (attributes.occlusions || []) as Occlusion[];

    console.log("###Occlusions");
    console.log(JSON.stringify(occlusions));

    // Create occlusion paths
    occlusions.forEach((occlusion) => {
      const occlusionPathStrings: string[] = [];
      const occlusionPoints: SplinePoint[] = [];

      const topX = interpolateXForY(points as SplinePoint[], occlusion.top);
      const bottomX = interpolateXForY(points as SplinePoint[], occlusion.bottom);

      occlusionPoints.push({ x: topX, y: occlusion.top, r: default_line_width });
      occlusionPoints.push(
        ...(points as SplinePoint[]).filter((point) => point.y > occlusion.top && point.y < occlusion.bottom)
      );
      occlusionPoints.push({ x: bottomX, y: occlusion.bottom, r: default_line_width });

      for (let i = 0; i < occlusionPoints.length; i++) {
        const currPoint = occlusionPoints[i];

        if (i === 0) {
          occlusionPathStrings.push(`M${currPoint.x},${currPoint.y}`);
        } else {
          const prevPoint = occlusionPoints[i - 1];
          occlusionPathStrings.push(`L${currPoint.x},${currPoint.y}`);
        }
      }

      const occlusionPathString = occlusionPathStrings.join(" ");
      const occlusionPath = new fabric.Path(occlusionPathString, {
        stroke: "black",
        fill: "",
        // TODO: set the correct r value later
        strokeWidth: default_line_width * 8,
        opacity: opacity,
      });

      group.addWithUpdate(occlusionPath); // Add each occlusion path to the group
    });
  }

  return null;
};

function interpolateXForY(points: SplinePoint[], y: number): number {
  const p1 = points.find((point) => point.y <= y);
  const p2 = points.find((point) => point.y >= y);

  if (p1 && p2) {
    const t = (y - p1.y) / (p2.y - p1.y);
    return p1.x + t * (p2.x - p1.x);
  }

  return 0;
}

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
