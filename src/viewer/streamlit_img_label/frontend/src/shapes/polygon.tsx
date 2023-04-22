import React from "react";
import { fabric } from "fabric"
import { PolygonProps, ShapeRenderProps } from "./interfaces";
  
export const VanishingPoint: React.FC<ShapeRenderProps> = ({ shape, color, opacity, canvas }) => {
    const { points, label } = shape as PolygonProps

    const { x, y } = points[0]

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

export const Polygon: React.FC<ShapeRenderProps> = ({ shape, color, opacity, canvas }) => {
    const { points, label } = shape as PolygonProps
    const polygon = new fabric.Polygon(points, {
        fill: color,
        stroke: 'black',
        opacity: opacity,
        strokeWidth: 2,
    });
    canvas.add(polygon);

    return null;
}
