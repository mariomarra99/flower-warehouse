# Flower Warehouse

**Web app** for **data management** of a flower warehouse. **Frontend** in Javscript React (with HTML and CSS support), **backend** in Python, **database** in PostgreSQL. The goal is to create an **interactive map** of a warehouse, giving the possibility to both visualize its structure and manage the data of the objects. Another key feature is the ability to find the **optimal path** with **A***, one of the best pathfinding algorithm, which is useful in a warehouse context to optimize stack picking times.

**Demo video (click on the image)**:

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/qP94jvGTqAg/0.jpg)](https://www.youtube.com/watch?v=qP94jvGTqAg)

To get a comprehensive view of the program's capabilities and the extent of its development, I invite you to watch the video. It will be updated as the program develops. 

## Object definition

**Obstacle**: the basic unit of the map, a generic object that acts as **impediment** to the passage of a warehouse worker/forklift, etc. We don't care what it is in the real world. The **attributes** are the Cartesian position **(x, y)** in the map.

**Shelf**: unit that represents a **real-world shelf**. The information it stores is critical for our purposes. From a code perspective, they are also obstacles as they are impediments. The **attributes** are position **(x,y)**, **flower**, **color** and **quantity**.

The flower, color and quantity attributes have this name but are **free text** and **number**, so you can do whatever you want with them.

## Features
Here are the features currently available:
 - **Connect**: connects to the database via a backend request. If the database is empty it creates the right table else takes the saved map and displays it on the grid.
 -  **Add shelf/obstacle**: creates one or more shelves/obstacles based on the selected boxes. If it is creating a shelf, it asks to insert the corresponding instances.
 - **Remove shelf/obstacle**: removes one or more shelves/obstacle based on the selected boxes.
 - **Modify obstacle**: makes you able to edit instances of the selected shelves.
 - **Flowers available**: prints the contents of the selected cells or all cells if pressed without selecting a cell.
 - **Withdrawal Simulation**: simulates picking the shelves select returning the fastest path to follow using A* . It works by selecting a start point and one or more goals.
 - **Reset Map**: restarts the set of the map. 

## Installation requirements and setup
Required softwares/languages and libraries:
 - Node.js, npm
 - React
 - Axios
 - Python3
 - Flask
 - Flask-Cors
 - PostgreSQL

To launch the web app use 'npm run dev' in '..\src', 'python app.py' in '..\src\backend' for backend and create your server and database and insert your data on 'db_credentials.txt' in '..\src\backend'.

