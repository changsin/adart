import React from "react";
import { fabric } from "fabric"
import { BoxPoint, ShapeRenderProps } from "../interfaces";
import { sendSelectedShape } from "../streamlit-utils";

export const Box: React.FC<ShapeRenderProps> = ({ shape, color, opacity, canvas }) => {
    const {shape_id, points, label } = shape;
    const {x, y, w, h} = points[0] as BoxPoint
    if (label === "untagged") {
        console.log("Detected " + shape.label + " " + shape.shape_id + " " + { x, y, w, h });
        color = "red";
        console.log(shape)
    }
    const box = new fabric.Rect({
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
    })
    const text = new fabric.Text(label, {
        left: x,
        top: y + 20,
        fontFamily: "Arial",
        fontSize: 14,
        fontWeight: "bold",
        fill: color,
        opacity: opacity
    })
    const selectedBox = new fabric.Rect({
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
        selectable: false,
        visible: false,
        lockMovementX: true, // Set lockMovementX to true
        lockMovementY: true, // Set lockMovementY to true
        opacity: opacity
    })
    canvas.add(box)
    // canvas.add(text)
    canvas.add(selectedBox)

    box.on("mousedown", () => {
        canvas.discardActiveObject(); // Deselect any previously selected object
        console.log("selectedAnnotation")
        if (selectedBox.visible) {
            // If the annotation is already selected, deselect it
            box.trigger("deselected"); // Manually trigger the deselected event
            selectedBox.visible = false;
        } else {
            // Otherwise, select the annotation
            selectedBox.set({
            left: x,
            top: y,
            width: w,
            height: h,
            visible: true,
            });
            canvas.setActiveObject(selectedBox);
            box.trigger("selected"); // Manually trigger the selected event
        }
    });

    box.on("mouseup", (event) => {
        if (!event.target) {
        // If no object is clicked, deselect any selected object
        const activeObject = canvas.getActiveObject();
        if (activeObject === selectedBox) {
            box.trigger("deselected"); // Manually trigger the deselected event
            selectedBox.visible = false;
        }
        }
    });
    
    // Add a click event listener to show the highlight rectangle
    box.on("selected", () => {
        selectedBox.set({
        left: x,
        top: y,
        width: w,
        height: h,
        visible: true,
        });
        canvas.setActiveObject(selectedBox);

        console.log("selected " + shape)
        sendSelectedShape(shape)
    });

    // Add a click event listener to hide the highlight rectangle
    box.on("deselected", () => {
        selectedBox.visible = false;
    });

    return null;
};
