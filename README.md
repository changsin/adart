# ADaRT (AI Data Reviewing Tool)
ADaRT is a data reviewing tool written in Streamlit and React.

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
>cd view/streamlit_img_label/frontend
>npm install
>npm run build
```

