import React, { useEffect, useState } from "react"
import { Range, getTrackBackground } from 'react-range'
import {
    ComponentProps,
    Streamlit,
    withStreamlitConnection,
} from "streamlit-component-lib"
import { fabric } from "fabric"
import styles from "./StreamlitImgLabel.module.css"
import {
    BoxPoint,
    ShapeProps,
    PythonArgs,
} from "./interfaces";
import { Box } from "./shapes/box"
import { Polygon, VanishingPoint } from "./shapes/polygon"
import { Spline } from "./shapes/spline"
import { sendSelectedShape } from "./streamlit-utils"

const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState<string>("light")
    const [labels, setLabels] = useState<string[]>([])
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    const { canvasWidth, canvasHeight, shapes, shapeColor, imageData }: PythonArgs = props.args
    const [newBBoxIndex, setNewBBoxIndex] = useState<number>(shapes.length)
    const [opacity, setOpacity] = useState(0.3);
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
            // Add shapes to the canvas
            shapes.forEach((shape) => {
                if (shape.shapeType === "box") {
                    console.log(shape)
                    // const box = <Box shape={shape} color={shapeColor} opacity={opacity} canvas={canvas} />;
                    Box({shape, color: shapeColor, opacity, canvas});
                } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                    Spline({shape, color: shapeColor, opacity, canvas});
                } else if (shape.shapeType === "polygon") {
                    if (polygonVisible === true) {
                        Polygon({shape, color: "purple", opacity, canvas});
                    }
                } else if (shape.shapeType === "VP") {
                    VanishingPoint({shape, color: "red", opacity, canvas});
                } else {
                    console.warn(`Invalid shape "${shape.shapeType}" specified". Skipping...`)
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
    const untaggedBox = (shape_id: number): ShapeProps  => ({
        shape_id: shape_id,
        points: [{
            x: canvasWidth * 0.15 + newBBoxIndex * 3,
            y: canvasHeight * 0.15 + newBBoxIndex * 3,
            w: canvasWidth * 0.2,
            h: canvasHeight * 0.2,
        }],
        label: "untagged",
        shapeType: "box",
        attributes: null,
        verification_result: ({ error_code: "untagged", comment: null})
    });
            
    // Add new bounding box to the image
    const addBoxHandler = () => {
        const box = untaggedBox(newBBoxIndex)
        const rect = setNewBBoxIndex(newBBoxIndex + 1)
        shapes.push(box)
        canvas.add(
            new fabric.Rect({
                top: box.points[0].y,
                left: box.points[0].x,
                width: (box.points[0] as BoxPoint).w,
                height: (box.points[0] as BoxPoint).h,
                fill: "",
                objectCaching: true,
                stroke: "red",
                strokeWidth: 1,
                strokeUniform: true,
                hasRotatingPoint: false,
            })
        )
        sendSelectedShape(box)
    }

    // Remove the selected bounding box
    const removeBoxHandler = () => {
        const selectObject = canvas.getActiveObject()
        const selectIndex = canvas.getObjects().indexOf(selectObject)
        canvas.remove(selectObject)
        sendCoordinates(labels.filter((label, i) => i !== selectIndex))
    }

    const resetHandler = () => {
        clearHandler();
      
        shapes.forEach((shape) => {
          if (shape.shapeType === "box") {
            Box({ shape, color: shapeColor, opacity, canvas });
          } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
            Spline({ shape, color: shapeColor, opacity, canvas });
          } else if (shape.shapeType === "polygon" && polygonVisible === true) {
            Polygon({ shape, color: "purple", opacity, canvas });
          } else if (shape.shapeType === "VP") {
            VanishingPoint({ shape, color: "red", opacity, canvas });
          } else {
            console.warn(`Invalid shape "${shape}" specified". Skipping...`);
            return;
          }
        });
      };
      

    // Remove all the bounding boxes
    const clearHandler = () => {
        // setNewBBoxIndex(0)
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
