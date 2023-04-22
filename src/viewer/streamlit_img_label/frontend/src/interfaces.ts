export interface Point {
  x: number;
  y: number;
}

export interface SplinePoint extends Point {
  r: number;
}

export interface BoxPoint extends Point {
  w: number;
  h: number;
}

export interface VerificationResult {
  error_code: string;
  comment: string | null;
}

export interface Attributes {
  key: string;
  value: string;
}

export interface ShapeProps {
  shape_id: number;
  label: string;
  points: BoxPoint[] | SplinePoint[] | Point[]
  shapeType: "box" | "spline" | "boundary" | "polygon" | "VP";
  attributes: Attributes[] | null;
  verification_result: VerificationResult | null;
}

export interface ShapeRenderProps {
  shape: ShapeProps;
  color: string;
  opacity: number;
  canvas: fabric.Canvas;
}

export interface PythonArgs {
  canvasWidth: number
  canvasHeight: number
  shapes: ShapeProps[]
  shapeColor: string
  imageData: Uint8ClampedArray
}
