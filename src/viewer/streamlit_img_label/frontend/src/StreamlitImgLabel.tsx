import { useEffect, useState, useMemo } from "react"
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
    const [zoomLevel, setZoomLevel] = useState(1);


    const handleOpacityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const opacityValue = Number(event.target.value) / 100;
        setOpacity(opacityValue);
        canvas.renderAll();
    };
    
    const togglePolygonVisibility = (value: boolean) => {
        togglePolygon(value);
        canvas.renderAll();
    };
    /*
     * Translate Python image data to a JavaScript Image
     */
    var invisCanvas = document.createElement("canvas")
    var ctx = invisCanvas.getContext("2d")

    invisCanvas.width = canvasWidth
    invisCanvas.height = canvasHeight
  
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
      
    // create imageData object
    let dataUri: any
    if (ctx) {
        var idata = ctx.createImageData(canvasWidth, canvasHeight)

        // set our buffer as source
        // idata.data.set(decompressedData)
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
                let color = shapeColor;
                if (shape.verification_result?.error_code &&
                    shape.verification_result?.error_code.length > 0) {
                    color = "red";
                }
                if (shape.shapeType === "box") {
                // // const box = <Box shape={shape} color={shapeColor} opacity={opacity} canvas={canvas} />;
                  Box({shape, color: color, opacity, canvas});
                // FabricShape({shape, color: shapeColor, opacity, canvas});
                } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                    Spline({shape, color: color, opacity, canvas});
                } else if (shape.shapeType === "polygon" && polygonVisible === true) {
                    Polygon({shape, color: "purple", opacity, canvas});
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

    useEffect(() => {
        const handleMouseWheel = (event: fabric.IEvent) => {
            if (event.e instanceof WheelEvent) {
              const delta = event.e.deltaY;
              let zoom = canvas.getZoom();
              zoom *= 0.999 ** delta;
              if (zoom > 20) zoom = 20;
              if (zoom < 0.01) zoom = 0.01;
              const { x, y } = canvas.getPointer(event as any);
              canvas.zoomToPoint(new fabric.Point(x, y), zoomLevel);
              setZoomLevel(zoom);

              //   canvas.zoomToPoint({ x: event.e.offsetX, y: event.e.offsetY }, zoom);
              event.e.preventDefault();
              event.e.stopPropagation();
            }
          };
                                  
        canvas.on("mouse:wheel", handleMouseWheel);
    
        return () => {
            canvas.off("mouse:wheel", handleMouseWheel);
        };
    }, [canvas]);

    useEffect(() => {
        let isDragging = false;
        let lastX: number;
        let lastY: number;
    
        const handleMouseDown = (event: fabric.IEvent) => {
            isDragging = true;
            const pointer = canvas.getPointer(event.e);
            lastX = pointer.x;
            lastY = pointer.y;
        };
    
        const handleMouseMove = (event: fabric.IEvent) => {
            if (isDragging) {
                const pointer = canvas.getPointer(event.e);
                const deltaX = pointer.x - lastX;
                const deltaY = pointer.y - lastY;

                canvas.relativePan(new fabric.Point(deltaX, deltaY));

                lastX = pointer.x;
                lastY = pointer.y;
            }
        };
    
        const handleMouseUp = (event: fabric.IEvent) => {
            isDragging = false;
        };
    
        canvas.on("mouse:down", handleMouseDown);
        canvas.on("mouse:move", handleMouseMove);
        canvas.on("mouse:up", handleMouseUp);
    
        return () => {
            canvas.off("mouse:down", handleMouseDown);
            canvas.off("mouse:move", handleMouseMove);
            canvas.off("mouse:up", handleMouseUp);
        };
    }, [canvas]);
    
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
                <div>
                <input
                        type="range"
                        min="0"
                        max="100"
                        value={opacity * 100}
                        onChange={handleOpacityChange}
                        />
                        Opacity
                        {/* <canvas id="canvas"></canvas> */}
                    </div>
              </div>
        </>
    )
}

export default withStreamlitConnection(StreamlitImgLabel)
