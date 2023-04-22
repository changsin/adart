export interface BoxProps {
  shape_id: number
  top: number
  left: number
  width: number
  height: number
  label: string
  shapeType: "box"
}

export interface SplinePoint {
  x: number;
  y: number;
  r: number;
}

export interface SplineProps {
  shape_id: number
  points: SplinePoint[]
  label: string
  shapeType: "spline"
}

export interface BoundaryPoint {
  x: number;
  y: number;
  r: number;
}

export interface BoundaryProps {
  shape_id: number
  points: BoundaryPoint[]
  label: string
  shapeType: "boundary"
}

export interface PolygonPoint {
  x: number;
  y: number;
}

export interface PolygonProps {
  shape_id: number
  points: PolygonPoint[]
  label: string
  shapeType: "polygon"
}

export interface VPProps {
  shape_id: number
  points: PolygonPoint[]
  label: string
  shapeType: "VP"
}

export type ShapeProps = BoxProps | SplineProps | BoundaryProps | PolygonProps | VPProps

export interface ShapeRenderProps {
  shape: ShapeProps;
  color: string;
  opacity: number;
  canvas:  fabric.Canvas;
}

export interface PythonArgs {
  canvasWidth: number
  canvasHeight: number
  shapes: ShapeProps[]
  shapeColor: string
  imageData: Uint8ClampedArray
}
