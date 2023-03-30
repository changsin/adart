# DaRT (Data Reviewer Tool)
This is a new data reviewing tool written in Python using Streamlit for UI.

To run:
1. streamlit run main.py

# streamlit_app example
How to make a standalone executable from a streamlit app.
This is done through Electron following (How to Convert a Streamlit App to an .EXE Executable)[https://www.youtube.com/watch?v=3wZ7GRbr91g]

1. npm install
2. npm run dump .\streamlit_app\ -- -r .\requirements.txt   
3. npm run servewindows (to run from IDE)
4. npm run dist (to build a standalone Electron app)