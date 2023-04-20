import React, { useEffect, useState } from "react"
import { Range, getTrackBackground } from 'react-range'
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

interface VPProps {
    points: PolygonPoint[]
    label: string
    shapeType: "VP"
}

type ShapeProps = RectProps | SplineProps | BoundaryProps | PolygonProps | VPProps

interface PythonArgs {
    canvasWidth: number
    canvasHeight: number
    shapes: ShapeProps[]
    shapeColor: string
    imageData: Uint8ClampedArray
}

function createSplinePath(points: SplinePoint[], color: string): fabric.Object | undefined {
    // Create an empty path string
    let path = "";
    let default_width = 5;
  
    // If there are less than two points, return null
    if (points.length < 2) {
      return undefined;
    }
  
    const segments: fabric.Object[] = [];
  
    // Move to the first point
    path += `M ${points[0].x} ${points[0].y}`;
  
    // Create a spline through all the points
    if (points.length === 2) {
      // If there are only two points, create a straight line
      path += ` L ${points[1].x} ${points[1].y}`;
      const segment = new fabric.Path(path, {
        fill: "",
        stroke: color,
        strokeWidth: points[1].r || default_width,
      });
      segments.push(segment);
    } else {
      // Otherwise, create a Bezier spline with the control points at each end
      for (let i = 1; i < points.length - 2; i++) {
        const xc = (points[i].x + points[i + 1].x) / 2;
        const yc = (points[i].y + points[i + 1].y) / 2;
        const r = points[i].r;
        const segmentPath = `M ${points[i].x} ${points[i].y} Q ${points[i].x} ${points[i].y}, ${xc} ${yc} T ${points[i + 1].x} ${points[i + 1].y}`;
        const segment = new fabric.Path(segmentPath, {
          fill: "",
          stroke: color,
          strokeWidth: r || default_width,
        });
        segments.push(segment);
      }
      // Add the last point to the path
      path += ` Q ${points[points.length - 2].x} ${points[points.length - 2].y}, ${points[points.length - 1].x} ${points[points.length - 1].y}`;
      const lastSegment = new fabric.Path(path, {
        fill: "",
        stroke: color,
        strokeWidth: points[points.length - 1].r || default_width,
      });
      segments.push(lastSegment);
    }
  
    // Create a Fabric.js path object from the path string
    const group = new fabric.Group(segments, {
      selectable: true,
    });
  
    // Return the group object
    return group;
  }
  
  function drawControlPoints(points: SplinePoint[], color: string): fabric.Object[] {
    const controlPoints: fabric.Object[] = [];

    for (let i = 0; i < points.length; i++) {
        const x = points[i].x
        const y = points[i].y
        const x_offset = points[i].r / 2;
        const line_x = new fabric.Line([x - x_offset, y, x + x_offset, y], {
            stroke: 'black',
            strokeWidth: 2,
        });

        controlPoints.push(line_x)
    }

    return controlPoints;
}

function drawVanishingPoint(canvas: fabric.Canvas, points: PolygonPoint[]) {
    if (!canvas) return;

    const { x, y } = points[0]

    const x_offset = 40
    const y_offset = 20
    const line_x = new fabric.Line([x - x_offset, y, x + x_offset, y], {
        stroke: 'red',
        strokeWidth: 2,
    });
    const line_y = new fabric.Line([x, y - y_offset, x, y + y_offset], {
        stroke: 'red',
        strokeWidth: 2,
    });

    canvas.add(line_x);
    canvas.add(line_y);
}
  
const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState<string>("light")
    const [labels, setLabels] = useState<string[]>([])
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    const { canvasWidth, canvasHeight, shapes, shapeColor, imageData }: PythonArgs = props.args
    const [newBBoxIndex, setNewBBoxIndex] = useState<number>(0)
    const [opacity, setOpacity] = useState(1);
    const [polygonVisible, togglePolygon] = useState(false);

    const handleOpacityChange = (value: number) => {
        setOpacity(value);
      };
    
    const togglePolygonVisibility = (value: boolean) => {
        togglePolygon(value);
      };
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

                        sendSelectedShape(shape)
                    });
                
                    // Add a click event listener to hide the highlight rectangle
                    annotation.on("deselected", () => {
                        selectedAnnotation.visible = false;
                    });
                } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                    const { points, label } = shape
                    const splinePath = createSplinePath(points, shapeColor);
                    // If the spline is an instance of fabric.Object, add it to the canvas
                    if (splinePath && splinePath instanceof fabric.Object) {
                        canvas.add(splinePath);
                    }
                    const controlPoints = drawControlPoints(points, shapeColor)
                    controlPoints.forEach(((point) => {
                        canvas.add(point)
                    }))
                } else if (shape.shapeType === "polygon" && polygonVisible === true) {
                    const { points, label } = shape
                    const polygon = new fabric.Polygon(points, {
                        fill: 'purple',
                        stroke: 'black',
                        opacity: opacity,
                        strokeWidth: 2,
                    });
                    canvas.add(polygon);
                } else if (shape.shapeType === "VP") {
                    drawVanishingPoint(canvas, shape.points)
                } else {
                    console.warn(`Invalid shape "${shape}" specified". Skipping...`)
                    return
                }
            })
        }

        // Set labels
        setLabels(shapes.map((shape) => shape.label))

        Streamlit.setFrameHeight()

        canvas.renderAll()

    }, [canvas, canvasHeight, canvasWidth, imageData, shapes, shapeColor, props.args, opacity, polygonVisible])

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
            } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                const { points, label } = shape
                const splinePath = createSplinePath(points, shapeColor);
                if (splinePath && splinePath instanceof fabric.Object) {
                    canvas.add(splinePath);
                }
                const controlPoints = drawControlPoints(points, shapeColor)
                controlPoints.forEach(((point) => {
                    canvas.add(point)
                }))
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

    const sendSelectedShape = (shape: ShapeProps) => {
        Streamlit.setComponentValue({ shape })
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
      
        // Streamlit.setComponentValue({ rects })
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
                    onClick={() => togglePolygonVisibility(!polygonVisible)}
                >
                    {polygonVisible ? "Hide Polygons" : "Show Polygons"}
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
                <Range
                    step={0.1}
                    min={0}
                    max={1}
                    values={[opacity]}
                    onChange={(values) => handleOpacityChange(values[0])}
                    renderTrack={({ props, children }) => (
                        <div
                        {...props}
                        style={{
                            ...props.style,
                            height: '6px',
                            display: 'flex',
                            width: '100%',
                        }}
                        >
                        <div
                            ref={props.ref}
                            style={{
                            height: '6px',
                            width: '100%',
                            borderRadius: '4px',
                            background: getTrackBackground({
                                values: [opacity],
                                colors: ['#ccc', '#548BF4', '#ccc'],
                                min: 0,
                                max: 1,
                            }),
                            alignSelf: 'center',
                            }}
                        >
                            {children}
                        </div>
                        </div>
                    )}
                    renderThumb={({ props }) => (
                        <div
                        {...props}
                        style={{
                            ...props.style,
                            height: '16px',
                            width: '16px',
                            borderRadius: '50%',
                            backgroundColor: '#548BF4',
                            border: '1px solid #ccc',
                        }}
                        />
                    )}
                    />
            </div>
        </>
    )
}

export default withStreamlitConnection(StreamlitImgLabel)
