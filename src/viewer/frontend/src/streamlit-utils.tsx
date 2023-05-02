
import { ShapeProps } from "./interfaces"
import {
    Streamlit,
} from "streamlit-component-lib"

// send the selected shape to Streamlit python component.
export const sendSelectedShape = (shape: ShapeProps) => {
    Streamlit.setComponentValue({ shape })
}
