from flask import Flask
from models import db, ProductOwner, ScrumMaster, ProjectDetails, SprintCalendar, UserStories, Users, Tasks, UserRoles

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Agile_Dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return "Welcome to the Project Management System"

if __name__ == '__main__':
    app.run(debug=True)