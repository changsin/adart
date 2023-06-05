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

    console.log(JSON.stringify(occlusions));

    // Create occlusion paths
    occlusions.forEach((occlusion) => {
      const occlusionInnerPathStrings: string[] = [];
      const occlusionOuterPathStrings: string[] = [];
      const occlusionPoints: SplinePoint[] = [];
    
      const topPoint = interpolateSplinePointForY(points as SplinePoint[], occlusion.top);
      const bottomPoint = interpolateSplinePointForY(points as SplinePoint[], occlusion.bottom);

      occlusionPoints.push(topPoint);
      // occlusionPoints.push(
      //   ...(points as SplinePoint[]).filter((point) => point.y > occlusion.top && point.y < occlusion.bottom)
      // );
      occlusionPoints.push(bottomPoint);
    
      for (let i = 0; i < occlusionPoints.length; i++) {
        const currPoint = occlusionPoints[i];
        const currWidth = currPoint.r;
    
        const innerControlPoint = new fabric.Point(currPoint.x - currWidth, currPoint.y);
        const outerControlPoint = new fabric.Point(currPoint.x + currWidth, currPoint.y);
    
        if (i === 0) {
          occlusionInnerPathStrings.push(`M${innerControlPoint.x},${innerControlPoint.y}`);
          occlusionOuterPathStrings.push(`M${outerControlPoint.x},${outerControlPoint.y}`);
        } else {
          const prevPoint = occlusionPoints[i - 1];
          const prevWidth = prevPoint.r;
    
          const innerPrevControlPoint = new fabric.Point(prevPoint.x - prevWidth, prevPoint.y);
          const outerPrevControlPoint = new fabric.Point(prevPoint.x + prevWidth, prevPoint.y);
    
          occlusionInnerPathStrings.push(`C${innerPrevControlPoint.x},${innerPrevControlPoint.y} ${innerControlPoint.x},${innerControlPoint.y} ${innerControlPoint.x},${innerControlPoint.y}`);
          occlusionOuterPathStrings.push(`C${outerPrevControlPoint.x},${outerPrevControlPoint.y} ${outerControlPoint.x},${outerControlPoint.y} ${outerControlPoint.x},${outerControlPoint.y}`);
        }
      }

      const occlusionInnerPathString = occlusionInnerPathStrings.join(" ");
      const occlusionOuterPathString = occlusionOuterPathStrings.join(" ");
      // Fill the area between inner and outerPath with areaPath
      const occlusionReversedOuterPathString = occlusionOuterPathString
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

      const occlusionAreaPathString = `${occlusionInnerPathString} L${occlusionPoints[occlusionPoints.length - 1].x},${occlusionPoints[occlusionPoints.length - 1].y} ${occlusionReversedOuterPathString} Z`;

      const occlusionOpacity = 1.0;
      const occlusionInnerPath = new fabric.Path(occlusionInnerPathString, {
        stroke: "red",
        fill: "",
        strokeWidth: default_line_width,
        opacity: occlusionOpacity,
      });
    
      const occlusionOuterPath = new fabric.Path(occlusionOuterPathString, {
        stroke: "red",
        fill: "",
        strokeWidth: default_line_width,
        opacity: occlusionOpacity,
      });

      const occlusionAreaPath = new fabric.Path(occlusionAreaPathString, {
        stroke: '',
        fill: "black",
        opacity: occlusionOpacity,
      });

      group.addWithUpdate(occlusionInnerPath);
      group.addWithUpdate(occlusionOuterPath);
      group.addWithUpdate(occlusionAreaPath);
    });
  }

  return null;
};

function interpolateSplinePointForY(points: SplinePoint[], y: number): SplinePoint {
  let left = 0;
  let right = points.length - 1;

  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const midY = points[mid].y;

    if (midY === y) {
      return { ...points[mid] };
    } else if (midY < y) {
      left = mid + 1;
    } else {
      right = mid - 1;
    }
  }

  // make sure that the indices are within range
  left = Math.min(points.length - 1, left);
  right = Math.max(0, right);

  // Now, the left and right indices represent the adjacent points to the desired y-coordinate
  const prevPoint = points[right];
  const nextPoint = points[left];

  const t = (y - prevPoint.y) / (nextPoint.y - prevPoint.y);

  // Interpolate x value
  const interpolatedX = prevPoint.x + t * (nextPoint.x - prevPoint.x);

  // Interpolate r value
  const interpolatedR = prevPoint.r + t * (nextPoint.r - prevPoint.r);

  return { x: interpolatedX, y, r: interpolatedR };
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
