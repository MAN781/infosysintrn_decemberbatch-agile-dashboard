from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ProductOwner Model
class ProductOwner(db.Model):
    __tablename__ = 'ProductOwner'
    ProductOwnerId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Email = db.Column(db.String(100), unique=True)
    RoleName = db.Column(db.String(100))

    projects = db.relationship('ProjectDetails', backref='product_owner', lazy=True)


# ScrumMaster Model
class ScrumMaster(db.Model):
    __tablename__ = 'ScrumMasters'
    ScrumMasterID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(100), unique=True)
    Name = db.Column(db.String(100))
    ContactNumber = db.Column(db.String(15))

    sprints = db.relationship('SprintCalendar', backref='scrum_master', lazy=True)


# ProjectDetails Model
class ProjectDetails(db.Model):
    __tablename__ = 'ProjectDetails'
    ProjectId = db.Column(db.Integer, primary_key=True)
    ProductOwnerId = db.Column(db.Integer, db.ForeignKey('ProductOwner.ProductOwnerId'))
    ProjectName = db.Column(db.String(100))
    ProjectDescription = db.Column(db.Text)
    StartDate = db.Column(db.Date)
    EndDate = db.Column(db.Date)
    RevisedEndDate = db.Column(db.Date)
    Status = db.Column(db.String(50))

    user_stories = db.relationship('UserStories', backref='project', lazy=True)
    sprints = db.relationship('SprintCalendar', backref='project', lazy=True)


# SprintCalendar Model
class SprintCalendar(db.Model):
    __tablename__ = 'SprintCalendar'
    SprintId = db.Column(db.Integer, primary_key=True)
    ProjectId = db.Column(db.Integer, db.ForeignKey('ProjectDetails.ProjectId'))
    ScrumMasterID = db.Column(db.Integer, db.ForeignKey('ScrumMasters.ScrumMasterID'))
    SprintNo = db.Column(db.Integer)
    StartDate = db.Column(db.Date)
    EndDate = db.Column(db.Date)
    Velocity = db.Column(db.Integer)

    user_stories = db.relationship('UserStories', backref='sprint', lazy=True)


# UserStories Model
class UserStories(db.Model):
    __tablename__ = 'UserStories'
    UserStoryID = db.Column(db.Integer, primary_key=True)
    ProjectId = db.Column(db.Integer, db.ForeignKey('ProjectDetails.ProjectId'))
    SprintId = db.Column(db.Integer, db.ForeignKey('SprintCalendar.SprintId'))
    PlannedSprint = db.Column(db.Integer)
    ActualSprint = db.Column(db.Integer)
    Description = db.Column(db.Text)
    StoryPoint = db.Column(db.Integer)
    MOSCOW = db.Column(db.String(50))
    Dependency = db.Column(db.String(100))
    Assignee = db.Column(db.String(100))
    Status = db.Column(db.String(50))

    tasks = db.relationship('Tasks', backref='user_story', lazy=True)


# Users Model
class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(100), unique=True)
    Password = db.Column(db.String(100))
    Email = db.Column(db.String(100), unique=True)
    Role = db.Column(db.String(50))
    PhoneNumber = db.Column(db.String(15))
    Name = db.Column(db.String(100))

    tasks = db.relationship('Tasks', backref='assigned_user', lazy=True)


# Tasks Model
class Tasks(db.Model):
    __tablename__ = 'Tasks'
    TaskId = db.Column(db.Integer, primary_key=True)
    UserStoryID = db.Column(db.Integer, db.ForeignKey('UserStories.UserStoryID'))
    TaskName = db.Column(db.String(100))
    AssignedUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    TaskStatus = db.Column(db.String(50))


# UserRoles Model
class UserRoles(db.Model):
    __tablename__ = 'UserRoles'
    RoleID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    RoleName = db.Column(db.String(50))
