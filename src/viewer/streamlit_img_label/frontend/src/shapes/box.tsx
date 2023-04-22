import React from "react";
import { fabric } from "fabric"
import { BoxProps, ShapeRenderProps } from "../interfaces";
import { sendSelectedShape } from "../streamlit-utils";

export const Box: React.FC<ShapeRenderProps> = ({ shape, color, opacity, canvas }) => {
    const {shape_id, top, left, width, height, label } = shape as BoxProps;
    const annotation = new fabric.Rect({
        left,
        top,
        fill: "",
        width,
        height,
        objectCaching: true,
        stroke: color,
        strokeWidth: 1,
        strokeUniform: true,
        hasRotatingPoint: false,
        opacity: opacity
    })
    const text = new fabric.Text(label, {
            left: left,
            top: top + 20,
            fontFamily: "Arial",
            fontSize: 14,
            fontWeight: "bold",
            fill: color,
            opacity: opacity
        })
    const selectedAnnotation = new fabric.Rect({
            left,
            top,
            fill: "",
            width,
            height,
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
            left: left,
            top: top,
            width: width,
            height: height,
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
        left: left,
        top: top,
        width: width,
        height: height,
        visible: true,
        });
        canvas.setActiveObject(selectedAnnotation);

        sendSelectedShape(shape)
    });

    // Add a click event listener to hide the highlight rectangle
    annotation.on("deselected", () => {
        selectedAnnotation.visible = false;
    });

    return null;
};
