
## 📝 STICK

A habit-tracking web application for managing habits, creating journals and promoting habit building by visualizing results with calendar, streak data and charts.

## Table of Contents
- 🤖 Technologies
- 🌟 Features
- 📖 Set Up
- 🙋🏻‍♀️ About Me
## Technologies

- Backend: Python, Flask, SQL, PostgreSQL, SQLAlchemy
- Frontend: Javascript, React JS, HTML, CSS, Bootstrap, AJAX, JSON, Jinja2
- Libraries: FullCalendar, Chart.js
- API: Cloudinary, Inspiration Quote
## Features

Screenshots and video walk-through will be available soon.


## Set Up

To run this project, first clone or fork repository:

```bash
    git clone https://github.com/chansya/Project_STICK

```
Create and activate a virtual environment inside your directory

```bash
    virtualenv env
    source env/bin/activate

```
Install requirements

```bash
    pip3 install -r requirements.txt

```
Sign up to obtain keys for the Cloudinary API.
Save the keys in a file called secrets.sh using this format.

```bash
    export CLOUDINARY_KEY="YOUR_KEY_GOES_HERE"
    export CLOUDINARY_SECRET="YOUR_KEY_GOES_HERE"

```

Source your keys into your virtual environment:
```bash
    source secrets.sh

```
Run the app:
```bash
    python3 server.py
```




## About Me

👋 Hi I am Amy, a software engineer and a loving mom of one. This fullstack application is my capstone project at Hakcbright Academy, a 12-week immersive full-stack software engineering program. I am eager to learn more and build meaningful products to bring positive impacts.
