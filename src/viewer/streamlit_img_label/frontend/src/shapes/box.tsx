import React from "react";
import { fabric } from "fabric"
import { BoxPoint, ShapeProps, ShapeRenderProps } from "../interfaces";
import { sendSelectedShape } from "../streamlit-utils";

export const Box: React.FC<ShapeRenderProps> = ({ shape, color, opacity, canvas }) => {
    const {shape_id, points, label } = shape;
    const {x, y, w, h} = points[0] as BoxPoint
    const annotation = new fabric.Rect({
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
    const selectedAnnotation = new fabric.Rect({
            left: x,
            top: y,
            fill: "",
            width: w,
            height: h,
            objectCaching: true,
            stroke: color,
            strokeWidth: 10,
            strokeUniform: true,
            hasRotatingPoint: false,
            selectable: false,
            visible: false,
            lockMovementX: true, // Set lockMovementX to true
            lockMovementY: true, // Set lockMovementY to true
            opacity: opacity
        })
    canvas.add(annotation)
    // canvas.add(text)
    canvas.add(selectedAnnotation)

    annotation.on("mousedown", () => {
        canvas.discardActiveObject(); // Deselect any previously selected object
        console.log("selectedAnnotation")
        if (selectedAnnotation.visible) {
            // If the annotation is already selected, deselect it
            annotation.trigger("deselected"); // Manually trigger the deselected event
            selectedAnnotation.visible = false;
        } else {
            // Otherwise, select the annotation
            selectedAnnotation.set({
            left: x,
            top: y,
            width: w,
            height: h,
            visible: true,
            });
            canvas.setActiveObject(selectedAnnotation);
            annotation.trigger("selected"); // Manually trigger the selected event
        }
    });

    annotation.on("mouseup", (event) => {
        if (!event.target) {
        // If no object is clicked, deselect any selected object
        const activeObject = canvas.getActiveObject();
        if (activeObject === selectedAnnotation) {
            annotation.trigger("deselected"); // Manually trigger the deselected event
            selectedAnnotation.visible = false;
        }
        }
    });
    
    // Add a click event listener to show the highlight rectangle
    annotation.on("selected", () => {
        selectedAnnotation.set({
        left: x,
        top: y,
        width: w,
        height: h,
        visible: true,
        });
        canvas.setActiveObject(selectedAnnotation);

        console.log("selected " + shape)
        sendSelectedShape(shape)
    });

    // Add a click event listener to hide the highlight rectangle
    annotation.on("deselected", () => {
        selectedAnnotation.visible = false;
    });

    return null;
};
