import { fabric } from "fabric";
import { ShapeRenderProps, Point, BoxPoint } from "../interfaces";
import { sendSelectedShape } from "../streamlit-utils";

type FabricShapeType = 'box' | 'VP' | 'polygon';

type ShapeConfig = {
    [key in FabricShapeType]: {
        main: (points: Point[], color: string, opacity: number) => fabric.Object | fabric.Line[];
        selected: (points: Point[], color: string, opacity: number) => fabric.Object | null;
    };
};

const shapeConfig: ShapeConfig = {
    box: {
        main: (points: Point[], color: string, opacity: number) => {
            const {x, y, w, h} = points[0] as BoxPoint
            return new fabric.Rect({
                left: x,
                top: y,
                fill: "",
                width: w,
                height: h,
                objectCaching: true,
                stroke: color,
                strokeWidth: 1,
                strokeUniform: true,
                hasRotatingPoint: false,
                opacity: opacity
            });
        },
        selected: (points: Point[], color: string, opacity: number) => {
            const {x, y, w, h} = points[0] as BoxPoint
            return new fabric.Rect({
                left: x,
                top: y,
                fill: "",
                width: w,
                height: h,
                objectCaching: true,
                stroke: color,
                strokeWidth: 5,
                strokeUniform: true,
                hasRotatingPoint: false,
                opacity: opacity,
                visible: false
            });
        }
    },
    VP: {
        main: (points: Point[], color: string, opacity: number) => {
            const { x, y } = points[0];
            const x_offset = 40;
            const y_offset = 20;
            const line_x = new fabric.Line([x - x_offset, y, x + x_offset, y], {
                stroke: "red",
                strokeWidth: 1,
                opacity: opacity,
            });
            const line_y = new fabric.Line([x, y - y_offset, x, y + y_offset], {
                stroke: "red",
                strokeWidth: 1,
                opacity: opacity,
            });
            return [line_x, line_y];
        },
        selected: () => null,
    },
    polygon: {
        main: (points: Point[], color: string, opacity: number) => {
            return new fabric.Polygon(points, {
                fill: color,
                stroke: color,
                opacity: opacity,
                strokeWidth: 1,
            });
        },
        selected: (points: Point[], color: string, opacity: number) => {
            return new fabric.Polygon(points, {
                fill: color,
                stroke: color,
                opacity: opacity,
                strokeWidth: 3,
                visible: false,
            });
        },
    },
};

export const FabricShape: React.FC<ShapeRenderProps> = ({ shape, color = 'purple', opacity = 0.3, canvas }) => {
    const { points, label } = shape;
    const { main, selected } = shapeConfig[label as FabricShapeType];

    const shapeObject = main(points, color, opacity);
    const selectedObject = selected(points, color, opacity);

    if (shapeObject instanceof fabric.Object && selectedObject instanceof fabric.Object) {
        canvas.add(shapeObject);
        shapeObject.on("mousedown", () => {
            canvas.discardActiveObject(); // Deselect any previously selected object
            if (selectedObject.visible) {
                // If the annotation is already selected, deselect it
                shapeObject.trigger("deselected"); // Manually trigger the deselected event
                selectedObject.visible = false;
            } else {
                // Otherwise, select the annotation
                selectedObject.set({ visible: true });
                canvas.setActiveObject(selectedObject);
                shapeObject.trigger("selected"); // Manually trigger the selected event
            }
        });
        shapeObject.on("mouseup", (event) => {
            if (!event.target) {
                // If no object is clicked, deselect any selected object
                const activeObject = canvas.getActiveObject();
                if (activeObject === selectedObject) {
                    shapeObject.trigger("deselected"); // Manually trigger the deselected event
                    selectedObject.visible = false;
                }
            }
        });
    
        // Add a click event listener to show the highlight rectangle
        shapeObject.on("selected", () => {
            selectedObject.set({ visible: true });
            canvas.setActiveObject(selectedObject);
    
            console.log("selected " + shape)
            sendSelectedShape(shape)
        });
      
        // Add a click event listener to hide the highlight rectangle
        shapeObject.on("deselected", () => {
            selectedObject.visible = false;
        });

    } else if (shapeObject instanceof Array) {
        canvas.add(shapeObject[0]);
        canvas.add(shapeObject[1]);
    }
  
    return null;
}