
import traceback
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///global.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ProductOwner Table
class ProductOwner(db.Model):
    __tablename__ = 'ProductOwner'
    ProductOwnerId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    RoleName = db.Column(db.String(255), nullable=False)

    # Relationships
    projects = db.relationship('ProjectDetails', backref='product_owner', lazy=True)

    def __repr__(self):
        return f"<ProductOwner {self.Name}>"

# ProjectDetails Table
class ProjectDetails(db.Model):
    __tablename__ = 'ProjectDetails'
    ProjectId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProductOwnerId = db.Column(db.Integer, db.ForeignKey('ProductOwner.ProductOwnerId'), nullable=False)
    ProjectName = db.Column(db.String(255), nullable=False)
    ProjectDescription = db.Column(db.Text)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    RevisedEndDate = db.Column(db.Date)
    Status = db.Column(db.String(100), default="Not Started")

    # Relationships
    sprints = db.relationship('SprintCalender', backref='project', lazy=True)
    user_stories = db.relationship('UserStories', backref='project', lazy=True)

    def __repr__(self):
        return f"<ProjectDetails {self.ProjectName}>"

# SprintCalender Table
class SprintCalender(db.Model):
    __tablename__ = 'SprintCalender'
    SprintId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProjectId = db.Column(db.Integer, db.ForeignKey('ProjectDetails.ProjectId'), nullable=False)
    ScrumMasterID = db.Column(db.Integer, db.ForeignKey('ScrumMasters.ScrumMasterID'), nullable=True)
    SprintNo = db.Column(db.Integer, nullable=True)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    Velocity = db.Column(db.Integer, default=0)

    # Relationships
    scrum_master = db.relationship('ScrumMasters', backref='sprints')
    user_stories = db.relationship('UserStories', backref='sprint', lazy=True)

    def __repr__(self):
        return f"<SprintCalender Sprint {self.SprintNo}>"

# ScrumMasters Table
class ScrumMasters(db.Model):
    __tablename__ = 'ScrumMasters'
    ScrumMasterID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String(255), nullable=False, unique=True)
    Name = db.Column(db.String(255), nullable=False)
    ContactNumber = db.Column(db.String(15))

    def __repr__(self):
        return f"<ScrumMasters {self.Name}>"

# Users Table
class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Role = db.Column(db.String(100), nullable=False)
    PhoneNumber = db.Column(db.String(15))
    Name = db.Column(db.String(255), nullable=False)

    # Relationships
    tasks = db.relationship('Tasks', backref='assigned_user', lazy=True)
    roles = db.relationship('UserRoles', backref='user', lazy=True)

    def __repr__(self):
        return f"<Users {self.Username}>"

# Tasks Table
class Tasks(db.Model):
    __tablename__ = 'Tasks'
    TaskId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserStoryID = db.Column(db.Integer, db.ForeignKey('UserStories.UserStoryID'), nullable=False)
    TaskName = db.Column(db.String(255), nullable=False)
    AssignedUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    TaskStatus = db.Column(db.String(100), default="Not Started")

    # Relationships
    user_story = db.relationship('UserStories', backref='tasks')

    def __repr__(self):
        return f"<Tasks {self.TaskName}>"

# UserRoles Table
class UserRoles(db.Model):
    __tablename__ = 'UserRoles'
    RoleID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    RoleName = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<UserRoles {self.RoleName}>"

# UserStories Table
class UserStories(db.Model):
    __tablename__ = 'UserStories'
    UserStoryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProjectId = db.Column(db.Integer, db.ForeignKey('ProjectDetails.ProjectId'), nullable=False)
    SprintId = db.Column(db.Integer, db.ForeignKey('SprintCalender.SprintId'), nullable=True)
    PlannedSprint = db.Column(db.Integer, nullable=False)
    ActualSprint = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.Text, nullable=False)
    StoryPoints = db.Column(db.Integer, nullable=False)
    MOSCOW = db.Column(db.String(50), nullable=False)
    Assignee = db.Column(db.String(255))
    Status = db.Column(db.String(100), default="Not Started")

    def __repr__(self):
        return f"<UserStories {self.Description[:20]}>"

class ProjectUsers(db.Model):
    __tablename__ = 'projectusers'

    user_id = db.Column(db.Integer, db.ForeignKey('Users.UserID'), primary_key=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('ProjectDetails.ProjectId'), primary_key=True, nullable=False)

    # Relationships (optional, for convenience in accessing related objects)
    user = db.relationship('Users', backref='project_associations')
    project = db.relationship('ProjectDetails', backref='user_associations')

    def __repr__(self):
        return f"<ProjectUsers(user_id={self.user_id}, project_id={self.project_id})>"



# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/product_owners', methods=['GET'])
def get_product_owners():
    owners = ProductOwner.query.all()
    return jsonify([
        {"id": owner.ProductOwnerId, "name": owner.Name}
        for owner in owners
    ])

@app.route('/api/scrum_masters' , methods=["GET"])
def scrumMasters():
    smasters = ScrumMasters.query.all()
    return jsonify([
        {"id" : smaster.ScrumMasterID, "name":smaster.Name} for smaster in smasters
    ])

@app.route('/api/users' , methods=["GET"])
def users():
    users = Users.query.all()
    return jsonify([
        {"id" : user.UserID, "name" : user.Username} for user in users
    ])

@app.route('/submit', methods=['POST'])
def submit_project_data():
    try:
        data = request.json
        print(data)

        # Convert date strings to Python datetime.date objects
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        revised_end_date = (
            datetime.strptime(data['revised_end_date'], '%Y-%m-%d').date()
            if data.get('revised_end_date')
            else None
        )

        # Add Project
        new_project = ProjectDetails(
            ProductOwnerId = data['product_owner_id'],
            ProjectName = data['project_name'],
            ProjectDescription = data['project_description'],
            StartDate = start_date,
            EndDate = end_date,
            RevisedEndDate = revised_end_date,
            Status = data['status']
        )
        db.session.add(new_project)
        db.session.commit()
        print("1st successfull")
        last_project = ProjectDetails.query.order_by(ProjectDetails.ProjectId.desc()).first()
        last_project_id = last_project.ProjectId if last_project else None

        selected_user_id = data['selected_user_ids'].split(',')
        for i in range(len(selected_user_id)):
            new_project_user = ProjectUsers(
                user_id = selected_user_id[i],
                project_id = last_project_id
            )
            db.session.add(new_project_user)
            db.session.commit()
        
        #sprint_no
        i = 1
        # Add Sprints and User Stories
        for sprint in data['sprints']:
            sprint_start_date = datetime.strptime(sprint['start_date'], '%Y-%m-%d').date()
            sprint_end_date = datetime.strptime(sprint['end_date'], '%Y-%m-%d').date()



            new_sprint = SprintCalender(
                ProjectId = last_project_id,
                SprintNo = i,
                ScrumMasterID = sprint['scrum_master_id'],
                StartDate = sprint_start_date,
                EndDate = sprint_end_date,
                Velocity = sprint['velocity']

            )
            i+=1
            db.session.add(new_sprint)
            db.session.commit()
            print("2nd successfull")

            for story in sprint['user_stories']:
                last_sprint = SprintCalender.query.order_by(SprintCalender.SprintId.desc()).first()
                last_sprint_id = last_sprint.SprintId if last_sprint else None
                new_story = UserStories(
                        ProjectId = last_project_id,
                        SprintId = last_sprint_id,
                        PlannedSprint = story['planned_sprint'],
                        ActualSprint = story['actual_sprint'],
                        Description = story['description'],
                        StoryPoints = story['story_points'],
                        MOSCOW = story['moscow'],
                        Assignee = story['assignee'],
                        Status = story['status']
                )
                db.session.add(new_story)
                db.session.commit()
                print("3rd successfull")

        return jsonify({"message": "Project, sprints, and user stories added successfully."}), 201

    except Exception as e:
        db.session.rollback()
        print("Full error traceback:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
