# ADaRT (AI Data Reviewing Tool)
ADaRT is a data reviewing tool written in Streamlit and React JS.

To run:
1.  Run the following
```markdown
>cd src
>pip install -r requirements.txt
>streamlit run home.py
```

# streamlit_app example
How to make a standalone executable from a streamlit app.
This is done through Electron following (How to Convert a Streamlit App to an .EXE Executable)[https://www.youtube.com/watch?v=3wZ7GRbr91g]

1. npm install
2. npm run dump .\streamlit_app\ -- -r .\requirements.txt   
3. npm run servewindows (to run from IDE)
4. npm run dist (to build a standalone Electron app)

# To build the frontend

```commandline
>cd src/viewer/frontend
>npm install
>npm run build
```

# Implementation Details

## 1. Rendering splines
A splines is a smooth curve in mathematics. They can be used to label road lanes and edges.
To implement them, they are represented as a collection of "control points" defined as x, y, and r.
1. r refers to the width
Usually, in the context of splines, 'r' refers to the 'radius' of a curve but, for our specific implementation,
we are using r to refer to the width of a line.
2. control points can be out-of-order
Due to the artifacts that can occur during annotation process, control points can be out-of-order.
To display them correctly, they are sorted when the xmls are parsed.
The fidelity between the original out-of-order control points and the sorted equivalents should be identical.


