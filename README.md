# ADaRT (AI Data Reviewing Tool)
ADaRT is an AI data reviewing tool that can help you find errors in annotation as well as generate visual analytics of the errors.
This tool will provide an easy way to parse the dataset (and the labels), and label and classify the errors.

# 1. To developers
The tool is written in Python (Streamlit) and React JS.
All source code is under src package.
Here are what each package does:
- **api**: api interfaces between the frontend and the backend.
- **backend**: SQLAlchemy is the ORM and Postgres the DB. They are in docker containers. See backend README for more details.
- **common:** common utility modules, constants, label conversion functions
- **models:** abstract interfaces of data labels, projects, tasks, and users
- **notebooks:** playground for POCs
- **pages:** web pages that take you to the rest of functions
- **viewer:** image viewer (frontend)

## 1.1. To build the frontend
**NB:** Make sure that your node version is **v16.20.0.** **v18** and later versions were found to have incompatibility problems.

```commandline
>cd src/viewer/frontend
>npm install
>npm run build
```

## 1.2. To run the app
Run the following
```markdown
>pip install -r requirements.txt
>streamlit run startup.py
```

## 1.3. To launch as a service
Assuming that you are running from a bran new Ubuntu server,

1. git clone
```commandline
>git clone https://github.com/changsin/adart.git
```
2. create a python virtual environment

```commandline
>python3 -m venv venv
```
3. Activate the virtual environment
```commandline
>source venv/bin/activate
```
4. Build the front end (see above 1.1.)

5. Open the port 8501 for TCP

```commandline
>sudo ufw allow 8501/tcp
>sudo ufw status
```
You should see something like this

```commandline
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere                  
8501/tcp                   ALLOW       Anywhere                  
22/tcp (v6)                ALLOW       Anywhere (v6)             
8501/tcp (v6)              ALLOW       Anywhere (v6)  
```
6. Launch streamlit app (see 1.2.)
You should see something like this
```commandline
streamlit run home.py 

Collecting usage statistics. To deactivate, set browser.gatherUsageStats to False.


  You can now view your Streamlit app in your browser.

  Network URL: http://192.168.12.54:8501
  External URL: http://221.148.188.81:8501
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


# Appendix
# 1.1. streamlit_app example
How to make a standalone executable from a streamlit app.
This is done through Electron following (How to Convert a Streamlit App to an .EXE Executable)[https://www.youtube.com/watch?v=3wZ7GRbr91g]

1. npm install
2. npm run dump .\streamlit_app\ -- -r .\requirements.txt   
3. npm run servewindows (to run from IDE)
4. npm run dist (to build a standalone Electron app)

