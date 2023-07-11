import React, { useEffect, useState, useMemo } from "react"
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
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
    ErrorType,
    VerificationResult
} from "./interfaces";
import { Box } from "./shapes/box"
import { Keypoint } from "./shapes/keypoint"
import { Polygon, VanishingPoint } from "./shapes/polygon"
import { Spline } from "./shapes/spline"
import { sendSelectedShape } from "./streamlit-utils"
import {displayAttributes} from "./shapes/shape-attributes"

const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState<string>("light")
    const [labels, setLabels] = useState<string[]>([])
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    const {canvasWidth, canvasHeight, shapes, shapeColor, imageData}: PythonArgs = props.args
    const [newBBoxIndex, setNewBBoxIndex] = useState<number>(shapes.length)
    const [opacity, setOpacity] = useState<number>(0.5);
    const [isInteractingWithBox, setIsInteractingWithBox] = useState(false);
    const [selectedShape, setSelectedShape] = useState<ShapeProps | null>(null);
    const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(selectedShape?.verification_result || { error_code: '', comment: '' });

    const [shapesInternal, setShapesInternal] = useState<ShapeProps[]>(shapes);
    const [checkedClassLabels, setCheckedClassLabels] = useState<string[]>([]);
    const [selectAllClassLabels, setSelectAllClassLabels] = useState(false);
    const [expandedLabels, setExpandedLabels] = useState<string[]>([]);
    const [checkedIndividualLabels, setCheckedIndividualLabels] = useState<string[]>(shapesInternal
        .filter((shape) => (shape.verification_result !== null) || (shape.label === 'spline') || (shape.label === 'VP'))
        .map((shape) => `${shape.label}-${shape.shape_id}`));

    const updateShapes = (newShapes: ShapeProps[]) => {
        setLabels(newShapes.map((shape) => shape.label));
        // Update any other relevant state variables
        // ...
        setShapesInternal(newShapes);
    };

    const handleExpandLabel = (label: string) => {
        setExpandedLabels((prevExpandedLabels) =>
          prevExpandedLabels.includes(label)
            ? prevExpandedLabels.filter((l) => l !== label)
            : [...prevExpandedLabels, label]
        );
    };

    const handleIndividualLabelToggle = (label: string) => {
        setCheckedIndividualLabels((prevCheckedIndividualLabels) => {
            if (prevCheckedIndividualLabels.includes(label)) {
                return prevCheckedIndividualLabels.filter((l) => l !== label);
            } else {
                return [...prevCheckedIndividualLabels, label];
            }
        });
    };

    const handleClassLabelToggle = (label: string) => {
        setCheckedClassLabels((prevCheckedClassLabels) => {
          if (prevCheckedClassLabels.includes(label)) {
            // Uncheck class label
            const updatedClassLabels = prevCheckedClassLabels.filter((l) => l !== label);
            // Uncheck all individual labels for the class
            const updatedIndividualLabels = checkedIndividualLabels.filter(
              (individualLabel) => {
                const [individualLabelClass] = individualLabel.split("-");
                return individualLabelClass !== label;
              }
            );
            setCheckedIndividualLabels(updatedIndividualLabels);
            return updatedClassLabels;
          } else {
            // Check class label
            const updatedClassLabels = [...prevCheckedClassLabels, label];
            // Check all individual labels for the class
            const updatedIndividualLabels = shapesInternal
              .filter((shape) => shape.label === label)
              .map((shape) => `${shape.label}-${shape.shape_id}`);
            setCheckedIndividualLabels((prevCheckedIndividualLabels) => [
              ...prevCheckedIndividualLabels,
              ...updatedIndividualLabels,
            ]);
            return updatedClassLabels;
          }
        });
    };

    const toggleSelectAllClassLabels = () => {
        setSelectAllClassLabels(!selectAllClassLabels);
        if (!selectAllClassLabels) {
            const classLabels = shapesInternal.map(
                (shape) => `${shape.label}`
            );
            const individualLabels = shapesInternal.map(
                (shape) => `${shape.label}-${shape.shape_id}`
            );
            setCheckedClassLabels(classLabels);
            setCheckedIndividualLabels(individualLabels);
        } else {
            setCheckedClassLabels([]);
            setCheckedIndividualLabels([]);
        }
    };

    const handleOpacityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const opacityValue = Number(event.target.value) / 100;
        setOpacity(opacityValue);
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
        if (is_error(shape) || shape.shapeType === "VP") {
            color = "red";
        } else if (shape.shapeType === "spline") {
            color = "green";
        } else if (shape.shapeType === "polygon") {
            color = "purple";
        } else if (shape.shapeType === "boundary") {
            color = "yellow";
        }
        return color;
    }

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
            clearHandler();

            // Add shapes to the canvas
            shapesInternal.forEach((shape) => {
                if (checkedIndividualLabels.includes(`${shape.label}-${shape.shape_id}`)) {
                    let color = pickColor(shape);
                    if (shape.shapeType === "box") {
                        Box({ shape, color: color, opacity, canvas, onSelectHandler: onSelectShapeHandler,});
                    } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                        Spline({ shape, color: color, opacity, canvas, onSelectHandler: onSelectShapeHandler,});
                    } else if (shape.shapeType === "polygon") {
                        Polygon({shape, color: color, opacity, canvas, onSelectHandler: onSelectShapeHandler,});
                    } else if (shape.shapeType === "VP") {
                        VanishingPoint({ shape, color: color, opacity, canvas });
                    } else if (shape.shapeType === "keypoint") {
                        Keypoint({shape, color: color, opacity, canvas, onSelectHandler: onSelectShapeHandler,});
                    } else {
                        console.warn(`Invalid shape "${shape}" specified". Skipping...`);
                        return;
                    }
                }
            })
 
            // Set labels
            setLabels(shapesInternal.map((shape) => shape.label))

            Streamlit.setFrameHeight()

            canvas.renderAll()
        }

    }, [canvas, canvasHeight, canvasWidth, imageData, shapesInternal, shapeColor, props.args, opacity, checkedClassLabels, checkedIndividualLabels])

    const onSelectShapeHandler = ((shape: ShapeProps, fabricShape: fabric.Object) => {
        console.log(`onSelectedShape ${JSON.stringify(shape)}`)
        sendSelectedShape(shape);
    
        setSelectedShape(shape);
        setVerificationResult(shape.verification_result);
    
        if (canvas) {
            canvas.remove(fabricShape);
            canvas.renderAll();
        }
    })

    const onSetVerificationResult = (verificationResult: VerificationResult| null) => {
        if (selectedShape) {
            const updatedShape: ShapeProps = {
              ...selectedShape,
              verification_result: verificationResult
            }
            setSelectedShape(updatedShape);
            sendSelectedShape(updatedShape);
            if (canvas) {
                canvas.renderAll();
            }
        }
    }
          
    // Create a default bounding box
    const untaggedBox = (shape_id: number): ShapeProps  => ({
        shape_id: shape_id,
        points: [{
            x: canvasWidth * 0.15 + newBBoxIndex * 3,
            y: canvasHeight * 0.15 + newBBoxIndex * 3,
            w: canvasWidth * 0.2,
            h: canvasHeight * 0.2,
        }],
        label: "Untagged",
        shapeType: "box",
        attributes: null,
        verification_result: ({ error_code: "Untagged", comment: null})
    });
            
    // Add new bounding box to the image
    const addBoxHandler = () => {
        const box = untaggedBox(newBBoxIndex);
        setNewBBoxIndex(newBBoxIndex + 1);
      
        if (canvas) {
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
      
            newRect.on('modified', () => {
                // Update the shape object when the rectangle is modified
                (box.points[0] as BoxPoint).x = newRect.left ?? 0;
                (box.points[0] as BoxPoint).y = newRect.top ?? 0;
                (box.points[0] as BoxPoint).w = newRect.width ?? 0;
                (box.points[0] as BoxPoint).h = newRect.height ?? 0;
            
                console.log("sending ");
                console.log(box);
                sendSelectedShape(box);
                shapesInternal.push(box);
                handleClassLabelToggle("Untagged");
                setIsInteractingWithBox(true);
            });
        
            newRect.on('mousedown', () => setIsInteractingWithBox(true));
            newRect.on('mouseup', () => setIsInteractingWithBox(false));
            newRect.on('mousemove', () => setIsInteractingWithBox(true));
        
            canvas.add(newRect);
        }
    };

    // Remove the selected bounding box
    const removeBoxHandler = () => {
        const selectedObject = canvas.getActiveObject();
        console.log(`removeObject ${JSON.stringify(selectedObject)}`);

        if (selectedShape) {
            if (selectedShape.attributes) {
                selectedShape.attributes["status"] = "DELETED";
            } else {
                selectedShape["attributes"] = {"status": "DELETED"};
            }
            console.log(selectedShape);
            sendSelectedShape(selectedShape);

            if (canvas) {
                canvas.remove(selectedObject);
                canvas.renderAll();
            }
        }
    }

    const resetHandler = () => {
        clearHandler();
      
        shapesInternal.forEach((shape) => {
            if (checkedIndividualLabels.includes(`${shape.label}-${shape.shape_id}`)) {
                let color = pickColor(shape);
                if (shape.shapeType === "box") {
                    Box({ shape, color: color, opacity, canvas, onSelectHandler: onSelectShapeHandler,});
                } else if (shape.shapeType === "spline" || shape.shapeType === "boundary") {
                    Spline({ shape, color: color, opacity, canvas, onSelectHandler: onSelectShapeHandler,});
                } else if (shape.shapeType === "polygon") {
                    Polygon({shape, color: color, opacity, canvas, onSelectHandler: onSelectShapeHandler,});
                } else if (shape.shapeType === "VP") {
                    VanishingPoint({ shape, color: color, opacity, canvas });
                } else {
                    console.warn(`Invalid shape "${shape}" specified". Skipping...`);
                    return;
                }
            }
        });
      };

    // Remove all the bounding boxes
    const clearHandler = () => {
        setNewBBoxIndex(shapes.length)
        canvas.getObjects().forEach((rect) => canvas.remove(rect))
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
        setMode(mode);
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
        <div>
            <div style={{ display: 'flex', flexDirection: 'row' }}>
                <div style={{ flexGrow: 1 }}>
                    <TransformWrapper disabled={isInteractingWithBox}>
                    <TransformComponent>
                        <canvas
                        id="c"
                        className={mode === 'dark' ? styles.dark : ''}
                        width={canvasWidth}
                        height={canvasHeight}
                        />
                    </TransformComponent>
                    </TransformWrapper>
                </div>
                <div style={{ marginLeft: '10px' }}>
                    <div>
                        <input
                        type="checkbox"
                        checked={selectAllClassLabels}
                        onChange={toggleSelectAllClassLabels}
                        />
                        Select All Shapes
                    </div>
                    <div>
                        {/* Expandable labels */}
                        {Array.from(new Set(labels)).map((label) => {
                            const labelCount = labels.filter((l) => l === label).length;
                            const labelText = `${label} (${labelCount})`;
                            const isExpanded = expandedLabels.includes(label);
                            const isClassLabelChecked = checkedClassLabels.includes(label);

                            return (
                            <div key={label}>
                                <label
                                style={{ marginRight: '10px', cursor: 'pointer' }}
                                onClick={() => handleExpandLabel(label)}
                                >
                                <strong>{isExpanded ? '-' : '+'}</strong> {labelText}
                                </label>
                                {isExpanded && (
                                <div style={{ marginLeft: '20px' }}>
                                {/* Class label */}
                                    {labelCount > 1 && (
                                        <label style={{ marginRight: '10px' }}>
                                            <input
                                            type="checkbox"
                                            checked={isClassLabelChecked}
                                            onChange={() => handleClassLabelToggle(label)}
                                            />
                                            Select All
                                        </label>
                                    )}
                                    {/* Individual labels */}
                                    {shapesInternal.map((l, index) => {
                                        if (l.label === label) {
                                            return (
                                            <label
                                                key={`${label}-${l.shape_id}`}
                                                style={{ marginRight: '10px' }}
                                            >
                                                <input
                                                type="checkbox"
                                                checked={checkedIndividualLabels.includes(`${l.label}-${l.shape_id}`)}
                                                onChange={() => handleIndividualLabelToggle(`${l.label}-${l.shape_id}`)}
                                                />
                                                {l.label}-{l.shape_id}
                                            </label>
                                            );
                                        }
                                        return null;
                                    })}
                                </div>
                                )}
                            </div>
                            );
                        })}
                    </div>
                    <div>
                        {selectedShape && (
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <label>
                                    {selectedShape.label}
                                </label>
                                <pre>{displayAttributes(selectedShape)}</pre>
                                <label>
                                    Error:
                                    <select
                                        value={verificationResult?.error_code ?? ''}
                                        onChange={(e) => {
                                            const errorCodeValue = e.target.value as string;
                                            setVerificationResult((prevVerificationResult: VerificationResult | null): VerificationResult | null => ({
                                            ...prevVerificationResult,
                                            error_code: errorCodeValue !== '' ? errorCodeValue : '',
                                            comment: prevVerificationResult?.comment !== undefined ? prevVerificationResult?.comment : ''
                                            }));
                                        }}
                                    >
                                    <option value="">None</option>
                                    <option value={ErrorType.DVE_MISS[1]}>{ErrorType.DVE_MISS[1]}</option>
                                    <option value={ErrorType.DVE_UNTAG[1]}>{ErrorType.DVE_UNTAG[1]}</option>
                                    <option value={ErrorType.DVE_OVER[1]}>{ErrorType.DVE_OVER[1]}</option>
                                    <option value={ErrorType.DVE_RANGE[1]}>{ErrorType.DVE_RANGE[1]}</option>
                                    <option value={ErrorType.DVE_ATTR[1]}>{ErrorType.DVE_ATTR[1]}</option>
                                    </select>
                                </label>
                                <label>
                                <input
                                    type="text"
                                    value={verificationResult?.comment ?? ''}
                                    onChange={(e) => {
                                        const commentValue = e.target?.value as string;
                                        setVerificationResult((prevVerificationResult: VerificationResult | null): VerificationResult | null => ({
                                            ...prevVerificationResult,
                                            error_code: prevVerificationResult?.error_code !== undefined ? prevVerificationResult?.error_code : '',
                                            comment: commentValue
                                        }));
                                    }}
                                    placeholder={verificationResult?.comment ? '' : 'Comment...'}
                                    />
                                </label>
                                <div>
                                    <button onClick={() => onSetVerificationResult(verificationResult)}>
                                    Set Error
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'row' }}>
                <div style={{ marginBottom: '10px' }}>
                    <button onClick={addBoxHandler} title="Mark Untagged object">Untagged</button>
                </div>
                <div style={{ marginBottom: '10px' }}>
                    <button onClick={removeBoxHandler} title="Delete Untagged label">Delete</button>
                </div>
                <div style={{ marginBottom: '10px' }}>
                    <button onClick={resetHandler}>Reset</button>
                </div>
                <div style={{ marginBottom: '10px' }}>
                    <button onClick={clearHandler}>Clear all</button>
                </div>
                <div style={{ marginBottom: '10px' }}>
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
        </div>
    );
}

export default withStreamlitConnection(StreamlitImgLabel)
