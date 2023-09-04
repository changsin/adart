// definitions of interfaces used in StreamlitImgLabel

export interface Point {
  x: number;
  y: number;
}

export interface SplinePoint extends Point {
  r: number;
}

export interface KeyPoint extends Point {
  z: number;
}

export interface BoxPoint extends Point {
  w: number;
  h: number;
}

// for now, comment is always null when sent through PythonArgs
// to reduce the amount of re-drawing the canvas
export interface VerificationResult {
  error_code: string;
  comment: string | null;
}

export const ErrorType = Object.freeze({
  DVE_NOERROR: [0, "No error"],
  DVE_MISS: [1, "Mis-tagged"],
  DVE_UNTAG: [2, "Untagged"],
  DVE_OVER: [3, "Over-tagged"],
  DVE_RANGE: [4, "Range_error"],
  DVE_ATTR: [5, "Attributes_error"],
});

export interface Occlusion {
  top: number;
  bottom: number;
}

export interface Attributes {
  [key: string]: string | number | Occlusion[] | null;
}

// interface to use between StreamlitImgLabel and shape FCs
export interface ShapeProps {
  shape_id: number;
  label: string;
  points: BoxPoint[] | SplinePoint[] | Point[]
  shapeType: "box" | "spline" | "boundary" | "polygon" | "segmentation" | "VP";
  attributes: Attributes | null;
  verification_result: VerificationResult | null;
}

// interface between StreamlitImgLabel and shape FCs
export interface ShapeRenderProps {
  shape: ShapeProps;
  color: string;
  opacity: number;
  canvas: fabric.Canvas;
  onSelectHandler?: (shape: ShapeProps, fabricsShape: fabric.Object) => void;
}

// interface between python and frontend
export interface PythonArgs {
  canvasWidth: number
  canvasHeight: number
  shapes: ShapeProps[]
  shapeColor: string
  imageData: Uint8ClampedArray
}
