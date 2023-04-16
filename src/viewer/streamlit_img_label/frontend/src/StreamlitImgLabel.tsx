import React, { useEffect, useState } from "react"
import {
    ComponentProps,
    Streamlit,
    withStreamlitConnection,
} from "streamlit-component-lib"
import { fabric } from "fabric"
import styles from "./StreamlitImgLabel.module.css"

// interface RectProps {
//     top: number
//     left: number
//     width: number
//     height: number
//     label: string
//     shape: "rectangle" | "spline"
//     radius?: number // Only used if shape is "spline"
// }

// interface SplineProps {
//     points: {x: number, y: number}[]
//     label: string
// }

interface RectProps {
    top: number
    left: number
    width: number
    height: number
    label: string
    shapeType: "rectangle"
}

interface SplineProps {
    points: Array<{ x: number; y: number }>
    radius: number
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

function getSplinePath(points: number[][], radius: number): string {
    const path = new Path2D();
    const firstPoint = points[0];
    path.moveTo(firstPoint[0] + radius, firstPoint[1]);
  
    for (let i = 1; i < points.length - 2; i++) {
      const currentPoint = points[i];
      const nextPoint = points[i + 1];
      const cp = [
        currentPoint[0] + (nextPoint[0] - currentPoint[0]) / 2,
        currentPoint[1] + (nextPoint[1] - currentPoint[1]) / 2,
      ];
  
      path.arcTo(cp[0], cp[1], nextPoint[0] + radius, nextPoint[1], radius);
    }
  
    // Draw the last two points as a straight line
    const secondLastPoint = points[points.length - 2];
    const lastPoint = points[points.length - 1];
    path.lineTo(lastPoint[0], lastPoint[1]);
    path.lineTo(secondLastPoint[0], secondLastPoint[1]);
  
    // Draw arcs for the rounded corners
    path.arcTo(
      lastPoint[0] - radius,
      lastPoint[1],
      lastPoint[0] - radius,
      lastPoint[1] + radius,
      radius
    );
    path.arcTo(
      lastPoint[0] - radius,
      lastPoint[1] + 2 * radius,
      lastPoint[0],
      lastPoint[1] + 2 * radius,
      radius
    );
    path.arcTo(
      lastPoint[0] + radius,
      lastPoint[1] + 2 * radius,
      lastPoint[0] + radius,
      lastPoint[1] + radius,
      radius
    );
    path.arcTo(
      lastPoint[0] + radius,
      lastPoint[1],
      lastPoint[0],
      lastPoint[1],
      radius
    );
  
    // Close the path
    path.closePath();
  
    return path.toString();
  }
  
const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState<string>("light")
    const [labels, setLabels] = useState<string[]>([])
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    // const { canvasWidth, canvasHeight, imageData }: PythonArgs = props.args
    const { canvasWidth, canvasHeight, imageData, shapes, boxColor }: PythonArgs = props.args
    const [newBBoxIndex, setNewBBoxIndex] = useState<number>(0)
    console.log(props)

  
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
        if (!canvas) {
        // Create a new canvas if it doesn't exist yet
        const canvasTmp = new fabric.Canvas("c", {
            enableRetinaScaling: false,
            backgroundImage: dataUri,
            uniScaleTransform: true,
        })
        setCanvas(canvasTmp)

        // Add shapes to the canvas
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
                // const spline = new fabric.Path(getSplinePath(props.points.map(({x, y}) => [x, y]), props.radius), {
                //     left: props.left,
                //     top: props.top,
                //     fill: "",
                //     objectCaching: true,
                //     stroke: props.boxColor,
                //     strokeWidth: 1,
                //     strokeUniform: true,
                //     hasRotatingPoint: false,
                //     lockUniScaling: true,
                //   });
                canvasTmp.add(spline)
                // const path = getSplinePath(points, radius)
                // canvasTmp.add(
                //     new fabric.Path(path, {
                //         fill: "",
                //         stroke: boxColor,
                //         strokeWidth: 1,
                //         objectCaching: true,
                //         hasRotatingPoint: false,
                //     })
                // )
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

        setCanvas(canvasTmp)
        // Set labels
        setLabels(shapes.map((shape) => shape.label))

        Streamlit.setFrameHeight()
        }
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

    // // Reset the bounding boxes
    // const resetHandler = () => {
    //     clearHandler()
    //     const { rects, boxColor }: PythonArgs = props.args
    //     rects.forEach((rect) => {
    //         const { top, left, width, height, label } = rect;
    //         canvas.add(
    //             new fabric.Rect({
    //                 left,
    //                 top,
    //                 fill: "",
    //                 width,
    //                 height,
    //                 objectCaching: true,
    //                 stroke: boxColor,
    //                 strokeWidth: 1,
    //                 strokeUniform: true,
    //                 hasRotatingPoint: false,
    //             })
    //         );
    //         canvas.add(
    //             new fabric.Text(label, {
    //                 left: left,
    //                 top: top + 20,
    //                 fontFamily: "Arial",
    //                 fontSize: 14,
    //                 fontWeight: "bold",
    //                 fill: "black",
    //             })
    //         );
    //     });
    //     sendCoordinates(labels)
    // }

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

    // Update the bounding boxes when modified
    useEffect(() => {
        if (!canvas) {
            return
        }
        const handleEvent = () => {
            canvas.renderAll()
            sendCoordinates(labels)
        }

        canvas.on("object:modified", handleEvent)
        return () => {
            canvas.off("object:modified")
        }
    })

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
                {/* <button
                    className={mode === "dark" ? styles.dark : ""}
                    onClick={resetHandler}
                >
                    Reset
                </button> */}
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
