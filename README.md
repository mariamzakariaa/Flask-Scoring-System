# Flask Scoring System 

A Flask-based scoring system I built to experiment and learn Flask development hands-on. The app allows managing participants, resetting competitions, and displaying a leaderboard. It is functional but incomplete, serving as a sandbox for practicing web app concepts.

## Features
- Add / delete participants dynamically
- Reset competition to clear all scores
- Leaderboard display with cumulative scores
- Session-based rounds tracking
- Templates for dynamic HTML rendering
- Partial SQLAlchemy integration for persistent storage

## Technical Highlights
- Flask routing, GET/POST handling, and session management
- HTML templating with Jinja2
- SQLAlchemy ORM setup and relational models (`Participant` and `Score`)
- Flash messages for real-time feedback
- JSON data loading for questions
- Form handling and validation

## Limitations / Work in Progress
- Score addition via forms partially implemented
- Minimal UI; not production-ready
- Authentication and multi-user support not implemented
- Some routes are placeholders for further exploration

## Usage
1. Clone the repository  
2. Install dependencies: `pip install flask flask_sqlalchemy`  
3. Run the app: `python main.py`  
4. Access the app at `http://127.0.0.1:5000/`  

> This project was built for personal learning and experimentation. It is functional but intentionally a sandbox to explore Flask fundamentals and web development concepts.
