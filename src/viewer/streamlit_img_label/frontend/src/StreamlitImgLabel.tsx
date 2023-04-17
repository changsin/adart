import React, { useEffect, useState } from "react"
import {
    ComponentProps,
    Streamlit,
    withStreamlitConnection,
} from "streamlit-component-lib"
import { fabric } from "fabric"
import styles from "./StreamlitImgLabel.module.css"

interface RectProps {
    top: number
    left: number
    width: number
    height: number
    label: string
    shapeType: "rectangle"
}

interface SplinePoint {
    x: number;
    y: number;
    r: number;
}

interface SplineProps {
    points: SplinePoint[]
    label: string
    shapeType: "spline"
}

type ShapeProps = RectProps | SplineProps

interface PythonArgs {
    canvasWidth: number
    canvasHeight: number
    shapes: ShapeProps[]
    boxColor: string
    imageData: Uint8ClampedArray
}

function getSplinePath(points: SplinePoint[]): string {
  const path = ["M", points[0].x, points[0].y];

  for (let i = 1; i < points.length - 2; i++) {
    const xc = (points[i].x + points[i + 1].x) / 2;
    const yc = (points[i].y + points[i + 1].y) / 2;
    const radius = (points[i].r + points[i + 1].r) / 2;
    const angle = Math.atan2(points[i + 1].y - points[i].y, points[i + 1].x - points[i].x);
    const controlX = xc - radius * Math.sin(angle);
    const controlY = yc + radius * Math.cos(angle);
    path.push("Q", points[i].x, points[i].y, controlX, controlY);
  }

  // curve through the last two points
  const secondLast = points[points.length - 2];
  const last = points[points.length - 1];
  const radius = (secondLast.r + last.r) / 2;
  const angle = Math.atan2(last.y - secondLast.y, last.x - secondLast.x);
  const controlX = last.x + radius * Math.sin(angle);
  const controlY = last.y - radius * Math.cos(angle);
  path.push("Q", secondLast.x, secondLast.y, controlX, controlY);

  return path.join(" ");
}

function createSplinePath(points: SplinePoint[], color: string): fabric.Path {
  const pathData = getSplinePath(points);
  const options = {
    fill: "",
    stroke: color,
    strokeWidth: 2,
  };
  const path = new fabric.Path(pathData, options);
  return path;
}

const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState<string>("light")
    const [labels, setLabels] = useState<string[]>([])
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    // const { canvasWidth, canvasHeight, imageData }: PythonArgs = props.args
    const { canvasWidth, canvasHeight, shapes, boxColor, imageData }: PythonArgs = props.args
    const [newBBoxIndex, setNewBBoxIndex] = useState<number>(0)
  
    /*
     * Translate Python image data to a JavaScript Image
     */
    var invisCanvas = document.createElement("canvas")
    var ctx = invisCanvas.getContext("2d")

    invisCanvas.width = canvasWidth
    invisCanvas.height = canvasHeight

    // create imageData object
    let dataUri: any
    if (ctx) {
        var idata = ctx.createImageData(canvasWidth, canvasHeight)

        // set our buffer as source
        idata.data.set(imageData)

        // update canvas with new data
        ctx.putImageData(idata, 0, 0)
        dataUri = invisCanvas.toDataURL()
    } else {
        dataUri = ""
    }

    // Initialize canvas on mount and add shapes
    useEffect(() => {
        const canvasTmp = new fabric.Canvas("c", {
            enableRetinaScaling: false,
            backgroundImage: dataUri,
            uniScaleTransform: true,
        })
        setCanvas(canvasTmp)
    }, [dataUri])


    // Add shapes to the canvas
    useEffect(() => {
        if (canvas) {
            const { shapes, boxColor }: PythonArgs = props.args
            // console.log("shapes")
            // console.log(shapes)
            // Add shapes to the canvas
            shapes.forEach((shape) => {
                if (shape.shapeType === "rectangle") {
                    const { top, left, width, height, label } = shape

                    const annotation = new fabric.Rect({
                            left,
                            top,
                            fill: "",
                            width,
                            height,
                            objectCaching: true,
                            stroke: boxColor,
                            strokeWidth: 1,
                            strokeUniform: true,
                            hasRotatingPoint: false
                        })
                    const text = new fabric.Text(label, {
                            left: left,
                            top: top + 20,
                            fontFamily: "Arial",
                            fontSize: 14,
                            fontWeight: "bold",
                            fill: boxColor,
                        })
                    const selectedAnnotation = new fabric.Rect({
                            left,
                            top,
                            fill: "",
                            width,
                            height,
                            objectCaching: true,
                            stroke: boxColor,
                            strokeWidth: 10,
                            strokeUniform: true,
                            hasRotatingPoint: false,
                            selectable: false,
                            visible: false,
                            lockMovementX: true, // Set lockMovementX to true
                            lockMovementY: true // Set lockMovementY to true
                        })
                    canvas.add(annotation)
                    canvas.add(text)
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
                    });
                
                    // Add a click event listener to hide the highlight rectangle
                    annotation.on("deselected", () => {
                        selectedAnnotation.visible = false;
                    });
                } else if (shape.shapeType === "spline") {
                    const { points, label } = shape
                    const splinePath = createSplinePath(points, boxColor);
                    canvas.add(splinePath);

                    canvas.add(
                        new fabric.Text(label, {
                            left: points[0].x,
                            top: points[0].y - 20,
                            fontFamily: "Arial",
                            fontSize: 14,
                            fontWeight: "bold",
                            fill: boxColor,
                        })
                    )
                } else {
                    console.warn(`Invalid shape "${shape}" specified". Skipping...`)
                    return
                }
            })
        }

        // Set labels
        setLabels(shapes.map((shape) => shape.label))

        // setCanvas(canvasTmp)

        Streamlit.setFrameHeight()

    }, [canvas, canvasHeight, canvasWidth, imageData, shapes, boxColor])

    // Create defualt bounding box
    const defaultBox = () => ({
        left: canvasWidth * 0.15 + newBBoxIndex * 3,
        top: canvasHeight * 0.15 + newBBoxIndex * 3,
        width: canvasWidth * 0.2,
        height: canvasHeight * 0.2,
    })

    // Add new bounding box to be image
    const addBoxHandler = () => {
        const box = defaultBox()
        setNewBBoxIndex(newBBoxIndex + 1)
        canvas.add(
            new fabric.Rect({
                ...box,
                fill: "",
                objectCaching: true,
                stroke: props.args.boxColor,
                strokeWidth: 1,
                strokeUniform: true,
                hasRotatingPoint: false,
            })
        )
        sendCoordinates([...labels, ""])
    }

    // Remove the selected bounding box
    const removeBoxHandler = () => {
        const selectObject = canvas.getActiveObject()
        const selectIndex = canvas.getObjects().indexOf(selectObject)
        canvas.remove(selectObject)
        sendCoordinates(labels.filter((label, i) => i !== selectIndex))
    }

    // Reset the shapes
    const resetHandler = () => {
        clearHandler()

        const canvasTmp = new fabric.Canvas("c", {
            enableRetinaScaling: false,
            backgroundImage: dataUri,
            uniScaleTransform: true,
        })

        shapes.forEach((shape) => {
            if (shape.shapeType === "rectangle") {
                const { top, left, width, height, label } = shape

                canvasTmp.add(
                    new fabric.Rect({
                        left,
                        top,
                        fill: "",
                        width,
                        height,
                        objectCaching: true,
                        stroke: boxColor,
                        strokeWidth: 1,
                        strokeUniform: true,
                        hasRotatingPoint: false,
                    })
                )
                canvasTmp.add(
                    new fabric.Text(label, {
                        left: left,
                        top: top + 20,
                        fontFamily: "Arial",
                        fontSize: 14,
                        fontWeight: "bold",
                        fill: boxColor,
                    })
                )
            } else if (shape.shapeType === "spline") {
                const { points, radius, label } = shape
                const spline = new fabric.Path(
                    getSplinePath(
                      shape.points.map(({ x, y }) => [x, y]),
                      shape.radius
                    ),
                    {
                      fill: "",
                      stroke: boxColor,
                      strokeWidth: 1,
                      strokeUniform: true,
                      hasRotatingPoint: false,
                    }
                  );
                canvasTmp.add(spline)

                canvasTmp.add(
                    new fabric.Text(label, {
                        left: points[0].x,
                        top: points[0].y - 20,
                        fontFamily: "Arial",
                        fontSize: 14,
                        fontWeight: "bold",
                        fill: boxColor,
                    })
                )
            } else {
                console.warn(`Invalid shape "${shape}" specified". Skipping...`)
                return
            }
        })
        sendCoordinates(labels)
    }

    // Remove all the bounding boxes
    const clearHandler = () => {
        setNewBBoxIndex(0)
        canvas.getObjects().forEach((rect) => canvas.remove(rect))
        sendCoordinates([])
    }

    // Send the coordinates of the rectangle back to streamlit.
    const sendCoordinates = (returnLabels: string[]) => {
        setLabels(returnLabels)
        const rects = canvas.getObjects().map((rect, i) => ({
            ...rect.getBoundingRect(),
            label: returnLabels[i],
        }))
        Streamlit.setComponentValue({ rects })
    }

    // Adjust the theme according to the system
    const onSelectMode = (mode: string) => {
        setMode(mode)
        if (mode === "dark") document.body.classList.add("dark-mode")
        else document.body.classList.remove("dark-mode")
    }

    useEffect(() => {
        // Add listener to update styles
        window
            .matchMedia("(prefers-color-scheme: dark)")
            .addEventListener("change", (e) =>
                onSelectMode(e.matches ? "dark" : "light")
            )

        // Setup dark/light mode for the first time
        onSelectMode(
            window.matchMedia("(prefers-color-scheme: dark)").matches
                ? "dark"
                : "light"
        )

        // Remove listener
        return () => {
            window
                .matchMedia("(prefers-color-scheme: dark)")
                .removeEventListener("change", () => {})
        }
    }, [])

    return (
        <>
            <canvas
                id="c"
                className={mode === "dark" ? styles.dark : ""}
                width={canvasWidth}
                height={canvasHeight}
            />
            <div className={mode === "dark" ? styles.dark : ""}>
                <button
                    className={mode === "dark" ? styles.dark : ""}
                    onClick={addBoxHandler}
                >
                    Mark Untagged
                </button>
                <button
                    className={mode === "dark" ? styles.dark : ""}
                    onClick={removeBoxHandler}
                >
                    Remove select
                </button>
                <button
                    className={mode === "dark" ? styles.dark : ""}
                    onClick={resetHandler}
                >
                    Reset
                </button>
                <button
                    className={mode === "dark" ? styles.dark : ""}
                    onClick={clearHandler}
                >
                    Clear all
                </button>
            </div>
        </>
    )
}

export default withStreamlitConnection(StreamlitImgLabel)
