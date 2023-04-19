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
    shapeType: "box"
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

interface BoundaryPoint {
    x: number;
    y: number;
    r: number;
}

interface BoundaryProps {
    points: BoundaryPoint[]
    label: string
    shapeType: "boundary"
}

interface PolygonPoint {
    x: number;
    y: number;
}

interface PolygonProps {
    points: PolygonPoint[]
    label: string
    shapeType: "polygon"
}

type ShapeProps = RectProps | SplineProps | BoundaryProps | PolygonProps

interface PythonArgs {
    canvasWidth: number
    canvasHeight: number
    shapes: ShapeProps[]
    shapeColor: string
    imageData: Uint8ClampedArray
}

interface SplineSegment {
    startPoint: SplinePoint;
    endPoint: SplinePoint;
    width: number;
  }
  
function getSplineSegments(points: SplinePoint[]): SplineSegment[] {
    const segments: SplineSegment[] = [];
  
    for (let i = 1; i < points.length - 2; i++) {
      const xc = (points[i].x + points[i + 1].x) / 2;
      const yc = (points[i].y + points[i + 1].y) / 2;
      const width = (points[i].r + points[i + 1].r) / 2;
      const angle = Math.atan2(points[i + 1].y - points[i].y, points[i + 1].x - points[i].x);
  
      const segment: SplineSegment = {
        startPoint: { x: points[i].x, y: points[i].y, r: points[i].r},
        endPoint: { x: xc, y: yc, r: width },
        width: width
      };
  
      segments.push(segment);
  
      const controlX = xc - width * Math.sin(angle);
      const controlY = yc + width * Math.cos(angle);
  
      segment.endPoint = { x: points[i + 1].x, y: points[i + 1].y, r: width };
      segment.width = (points[i + 1].r + points[i + 2].r) / 2;
  
      segment.startPoint = { x: controlX, y: controlY, r: width };
      segments.push(segment);
    }
  
    // handle last segment separately
    const secondLast = points[points.length - 2];
    const last = points[points.length - 1];
    const width = (secondLast.r + last.r) / 2;
    const angle = Math.atan2(last.y - secondLast.y, last.x - secondLast.x);
    const xc = (secondLast.x + last.x) / 2;
    const yc = (secondLast.y + last.y) / 2;
  
    const segment: SplineSegment = {
      startPoint: { x: secondLast.x, y: secondLast.y, r: width },
      endPoint: { x: xc, y: yc, r: width },
      width: width
    };
  
    segments.push(segment);
  
    const controlX = xc + width * Math.sin(angle);
    const controlY = yc - width * Math.cos(angle);
  
    segment.endPoint = { x: last.x, y: last.y, r: width };
    segment.width = width;
  
    segment.startPoint = { x: controlX, y: controlY, r: width };
    segments.push(segment);
  
    return segments;
  }

function getSplinePaths(points: SplinePoint[]): string {
    const path = ["M", points[0].x, points[0].y];

    for (let i = 1; i < points.length - 2; i++) {
        const xc = (points[i].x + points[i + 1].x) / 2;
        const yc = (points[i].y + points[i + 1].y) / 2;
        const width = (points[i].r + points[i + 1].r) / 2;
        const angle = Math.atan2(points[i + 1].y - points[i].y, points[i + 1].x - points[i].x);
        const controlX = xc - width * Math.sin(angle);
        const controlY = yc + width * Math.cos(angle);
        path.push("Q", points[i].x, points[i].y, controlX, controlY);
    }

  // curve through the last two points
  const secondLast = points[points.length - 2];
  const last = points[points.length - 1];
  const width = (secondLast.r + last.r) / 2;
  const angle = Math.atan2(last.y - secondLast.y, last.x - secondLast.x);
  const controlX = last.x + width * Math.sin(angle);
  const controlY = last.y - width * Math.cos(angle);
  path.push("Q", secondLast.x, secondLast.y, controlX, controlY);

  return path.join(" ");
}

let opacity = 0.7;

function createSplinePath(points: SplinePoint[], color: string): fabric.Object {
    const segments = getSplineSegments(points);

    const paths = segments.map((segment) => {
      const pathData = `M ${segment.startPoint.x} ${segment.startPoint.y} Q ${segment.endPoint.x} ${segment.endPoint.y} ${segment.startPoint.x} ${segment.startPoint.y}`;
      const options = {
        fill: "",
        stroke: color,
        strokeWidth: segment.width,
        opacity: opacity
      };
      return new fabric.Path(pathData, options);
    });
  
    const group = new fabric.Group(paths);
  
    return group;
}

const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState<string>("light")
    const [labels, setLabels] = useState<string[]>([])
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    const { canvasWidth, canvasHeight, shapes, shapeColor, imageData }: PythonArgs = props.args
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
            const { shapes, shapeColor }: PythonArgs = props.args
            // Add shapes to the canvas
            shapes.forEach((shape) => {
                if (shape.shapeType === "box") {
                    const { top, left, width, height, label } = shape

                    const annotation = new fabric.Rect({
                            left,
                            top,
                            fill: "",
                            width,
                            height,
                            objectCaching: true,
                            stroke: shapeColor,
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
                            fill: shapeColor,
                            opacity: opacity
                        })
                    const selectedAnnotation = new fabric.Rect({
                            left,
                            top,
                            fill: "",
                            width,
                            height,
                            objectCaching: true,
                            stroke: shapeColor,
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
                    });
                
                    // Add a click event listener to hide the highlight rectangle
                    annotation.on("deselected", () => {
                        selectedAnnotation.visible = false;
                    });
                } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                    const { points, label } = shape
                    const splinePath = createSplinePath(points, shapeColor);
                    canvas.add(splinePath);
                } else if (shape.shapeType === "polygon") {
                    const { points, label } = shape
                    const polygon = new fabric.Polygon(points, {
                        fill: 'purple',
                        stroke: 'black',
                        opacity: opacity,
                        strokeWidth: 2,
                    });
                    canvas.add(polygon);
                } else {
                    console.warn(`Invalid shape "${shape}" specified". Skipping...`)
                    return
                }
            })
        }

        // Set labels
        setLabels(shapes.map((shape) => shape.label))

        Streamlit.setFrameHeight()

        sendCoordinates(labels)

    }, [canvas, canvasHeight, canvasWidth, imageData, shapes, shapeColor, props.args])

    // Create a default bounding box
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
                stroke: props.args.shapeColor,
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
            if (shape.shapeType === "box") {
                const { top, left, width, height, label } = shape

                canvasTmp.add(
                    new fabric.Rect({
                        left,
                        top,
                        fill: "",
                        width,
                        height,
                        objectCaching: true,
                        stroke: shapeColor,
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
                        fill: shapeColor,
                    })
                )
            } else if (shape.shapeType === "spline") {
                const { points, label } = shape
                const splinePath = createSplinePath(points, shapeColor);
                canvas.add(splinePath);
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

    const sendCoordinates = (returnLabels: string[]) => {
        setLabels(returnLabels)
        const objects = canvas.getObjects()
        const rects = objects.map((rect, i) => ({
          ...rect.getBoundingRect(),
          label: returnLabels[i],
          shapeType: 'box'
        })).filter(Boolean)
        
        if (returnLabels.length !== objects.length) {
          console.warn('The length of the returnLabels array does not match the number of objects on the canvas.')
        }
      
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
