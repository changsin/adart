import React, { useEffect, useState, useMemo, useRef } from "react"
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import {
    ComponentProps,
    Streamlit,
    withStreamlitConnection,
} from "streamlit-component-lib"
import { fabric } from "fabric"
import { inflateSync } from "zlib"
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
import { FabricShape } from "./shapes/fabric-shape"

const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState<string>("light")
    const [labels, setLabels] = useState<string[]>([])
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    const { canvasWidth, canvasHeight, shapes, shapeColor, imageData }: PythonArgs = props.args
    const [newBBoxIndex, setNewBBoxIndex] = useState<number>(shapes.length)
    const [polygonVisible, togglePolygon] = useState(false);
    const [opacity, setOpacity] = useState<number>(0.3);
    const [isInteractingWithBox, setIsInteractingWithBox] = useState(false);

    const handleOpacityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const opacityValue = Number(event.target.value) / 100;
        setOpacity(opacityValue);
        if (canvas) {
            canvas.renderAll();
        }
    };
    
    const togglePolygonVisibility = (value: boolean) => {
        togglePolygon(value);
        if (canvas) {
            canvas.renderAll();
        }
    };

    function is_error(shape: ShapeProps): boolean {
        if (shape.verification_result?.error_code &&
            shape.verification_result?.error_code.length > 0) {
            return true;
        }
        return false;
    }

    function pickColor(shape: ShapeProps): string {
        let color = shapeColor;
        if (is_error(shape)) {
            color = "red";
        } else if (shape.shapeType === "polygon") {
            color = "purple";
        } else if (shape.shapeType === "boundary") {
            color = "yellow";
        }
        return color;
    }
      
    // // Decompress imageData on mount
    // const [decompressedData, setDecompressedData] = useState<Uint8ClampedArray>(
    //     new Uint8ClampedArray()
    // );
    // // useEffect(() => {
    // //     // decompress imageData using zlib
    // //     const compressedArray = new Uint8Array(imageData);
    // //     const compressedBuffer = Buffer.from(compressedArray);
    // //     const decompressedArray = inflateSync(compressedBuffer);
    // //     const decompressedData = new Uint8ClampedArray(decompressedArray);
    // //     setDecompressedData(decompressedData);
    // // }, [imageData]);

    // const decompressedImageData = useMemo(() => {
    //     // decompress imageData using zlib
    //     const compressedArray = new Uint8Array(imageData);
    //     const compressedBuffer = Buffer.from(compressedArray);
    //     const decompressedArray = inflateSync(compressedBuffer);
    //     return new Uint8ClampedArray(decompressedArray);
    // }, [imageData]);
      
    // useEffect(() => {
    //     setDecompressedData(decompressedImageData);
    // }, [decompressedImageData]);
      
    /*
     * Translate Python image data to a JavaScript Image
     */
    var invisCanvas = document.createElement("canvas")
    var ctx = invisCanvas.getContext("2d")

    invisCanvas.width = canvasWidth
    invisCanvas.height = canvasHeight
  
    // // create imageData object
    const canvasDataUri = useMemo(() => {
        let dataUri = ""
        if (ctx) {
          const idata = ctx.createImageData(canvasWidth, canvasHeight)
          idata.data.set(imageData)
          ctx.putImageData(idata, 0, 0)
          dataUri = invisCanvas.toDataURL()
        }
        return dataUri
    }, [imageData, ctx, canvasWidth, canvasHeight, invisCanvas])


    useEffect(() => {
        const canvasTmp = new fabric.Canvas("c", {
          enableRetinaScaling: false,
          backgroundImage: canvasDataUri,
          uniScaleTransform: true,
        })
        setCanvas(canvasTmp)
    }, [canvasDataUri])

      // Add shapes to the canvas
    useEffect(() => {
        if (canvas) {
            // Add shapes to the canvas
            shapes.forEach((shape) => {
                let color = pickColor(shape);
                if (shape.shapeType === "box") {
                // // const box = <Box shape={shape} color={shapeColor} opacity={opacity} canvas={canvas} />;
                    Box({shape, color: color, opacity, canvas});
                // FabricShape({shape, color: shapeColor, opacity, canvas});
                } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                    Spline({shape, color: color, opacity, canvas});
                } else if (shape.shapeType === "polygon") {
                    if (polygonVisible === true || is_error(shape)) {
                        Polygon({shape, color: color, opacity, canvas});
                    }
                } else if (shape.shapeType === "VP") {
                    VanishingPoint({shape, color: shapeColor, opacity, canvas});
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
        setNewBBoxIndex(newBBoxIndex + 1)

        const newRect = new fabric.Rect({
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

        // Attach event listeners to the rectangle object
        newRect.on('modified', () => {
            (box.points[0] as BoxPoint).x = newRect.left ?? 0;
            (box.points[0] as BoxPoint).y = newRect.top ?? 0;
            (box.points[0] as BoxPoint).w = newRect.width ?? 0;
            (box.points[0] as BoxPoint).h = newRect.height ?? 0;

            console.log("sending ");
            console.log(box);
            sendSelectedShape(box);
            shapes.push(box)
        })

        newRect.on('mousedown', () => setIsInteractingWithBox(true));
        newRect.on('mouseup', () => setIsInteractingWithBox(false));
        newRect.on('mousemove', () => setIsInteractingWithBox(true));
        
        canvas.add(newRect)
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
            let color = pickColor(shape);
            if (shape.shapeType === "box") {
                Box({ shape, color: color, opacity, canvas });
            } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                Spline({ shape, color: color, opacity, canvas });
            } else if (shape.shapeType === "polygon" && polygonVisible === true) {
                if (polygonVisible === true || is_error(shape)) {
                    Polygon({shape, color: color, opacity, canvas});
                }
            } else if (shape.shapeType === "VP") {
                VanishingPoint({ shape, color: color, opacity, canvas });
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
            <TransformWrapper disabled={isInteractingWithBox}
            >
                <TransformComponent>
                    <canvas
                            id="c"
                            className={mode === "dark" ? styles.dark : ""}
                            width={canvasWidth}
                            height={canvasHeight}
                        />
                </TransformComponent>
            </TransformWrapper>
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
                <div>
                <input
                    type="range"
                    min="0"
                    max="100"
                    value={opacity * 100}
                    onChange={handleOpacityChange}
                    />
                    Label Opacity
                    </div>
              </div>
        </>
    )
}

export default withStreamlitConnection(StreamlitImgLabel)
