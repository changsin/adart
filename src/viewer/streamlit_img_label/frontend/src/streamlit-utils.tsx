
import { ShapeProps } from "./interfaces"
import {
    Streamlit,
} from "streamlit-component-lib"

export const sendSelectedShape = (shape: ShapeProps) => {
    Streamlit.setComponentValue({ shape })
  }
