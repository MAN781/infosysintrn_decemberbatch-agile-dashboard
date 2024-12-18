from flask import Flask, render_template, Response
from models import db, ProductOwner, ScrumMaster, ProjectDetails, SprintCalendar, UserStories, Users, Tasks, UserRoles
from datetime import date
from datetime import datetime, timedelta
import random
import io
import pandas as pd
import matplotlib.pyplot as plt
import base64

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Agile_Dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Adding Product Owners
    if not ProductOwner.query.filter_by(Email="alice@company.com").first():
        product_owners = [
            ProductOwner(Name="Alice", Email="alice@company.com",
                         RoleName="Senior PO"),
            ProductOwner(Name="Bob", Email="bob@company.com", RoleName="PO"),
            ProductOwner(Name="Charlie", Email="charlie@company.com",
                         RoleName="Associate PO")
        ]
        db.session.add_all(product_owners)
        db.session.commit()

    # Adding Scrum Masters
    if not ScrumMaster.query.filter_by(Email="david@company.com").first():
        scrum_masters = [
            ScrumMaster(Name="David", Email="david@company.com",
                        ContactNumber="1234567890"),
            ScrumMaster(Name="Eve", Email="eve@company.com",
                        ContactNumber="0987654321"),
            ScrumMaster(Name="Frank", Email="frank@company.com",
                        ContactNumber="1122334455")
        ]
        db.session.add_all(scrum_masters)
        db.session.commit()

    # Adding Projects
    projects = [
        ProjectDetails(ProductOwnerId=1, ProjectName="Agile Dashboard", ProjectDescription="Develop an agile project management tool",
                       StartDate=date(2024, 1, 1), EndDate=date(2024, 12, 31), Status="In Progress"),
        ProjectDetails(ProductOwnerId=2, ProjectName="E-Commerce Platform", ProjectDescription="Create a scalable e-commerce platform",
                       StartDate=date(2024, 3, 1), EndDate=date(2024, 9, 30), Status="Not Started"),
        ProjectDetails(ProductOwnerId=3, ProjectName="Mobile App", ProjectDescription="Develop a mobile application",
                       StartDate=date(2024, 2, 1), EndDate=date(2024, 8, 31), Status="Completed"),
        ProjectDetails(ProductOwnerId=1, ProjectName="CRM System", ProjectDescription="Develop a customer relationship management system",
                       StartDate=date(2024, 4, 1), EndDate=date(2024, 10, 31), Status="In Progress"),
        ProjectDetails(ProductOwnerId=2, ProjectName="Data Analytics Platform", ProjectDescription="Create a data analytics platform",
                       StartDate=date(2024, 5, 1), EndDate=date(2024, 11, 30), Status="Not Started")
    ]
    db.session.add_all(projects)
    db.session.commit()

    # Adding Sprints
    if not SprintCalendar.query.filter_by(SprintNo=1, ProjectId=1).first():
        sprints = [
            SprintCalendar(ProjectId=1, ScrumMasterID=1, SprintNo=1, StartDate=date(
                2024, 1, 1), EndDate=date(2024, 1, 15), Velocity=20),
            SprintCalendar(ProjectId=1, ScrumMasterID=1, SprintNo=2, StartDate=date(
                2024, 1, 16), EndDate=date(2024, 1, 31), Velocity=22),
            SprintCalendar(ProjectId=2, ScrumMasterID=2, SprintNo=1, StartDate=date(
                2024, 3, 1), EndDate=date(2024, 3, 15), Velocity=18)
        ]
        db.session.add_all(sprints)
        db.session.commit()

    # Adding User Stories
    if not UserStories.query.filter_by(Description="Setup initial database schema").first():
        user_stories = [
            UserStories(ProjectId=1, SprintId=1, PlannedSprint=1, ActualSprint=1, Description="Setup initial database schema",
                        StoryPoint=5, MOSCOW="Must", Assignee="Dev1", Status="Completed"),
            UserStories(ProjectId=1, SprintId=1, PlannedSprint=1, ActualSprint=1, Description="Develop login module",
                        StoryPoint=8, MOSCOW="Must", Assignee="Dev2", Status="In Progress"),
            UserStories(ProjectId=1, SprintId=2, PlannedSprint=2, ActualSprint=0, Description="Integrate CI/CD pipeline",
                        StoryPoint=13, MOSCOW="Should", Assignee="Dev3", Status="Planned")
        ]
        db.session.add_all(user_stories)
        db.session.commit()

    # Adding Users
    if not Users.query.filter_by(UserName="Dev1").first():
        users = [
            Users(UserName="Dev1", Password="password1", Email="dev1@company.com",
                  Role="Developer", PhoneNumber="1231231234", Name="Developer One"),
            Users(UserName="Dev2", Password="password2", Email="dev2@company.com",
                  Role="Developer", PhoneNumber="4564564567", Name="Developer Two"),
            Users(UserName="QA1", Password="password3", Email="qa1@company.com",
                  Role="QA", PhoneNumber="7897897890", Name="QA One")
        ]
        db.session.add_all(users)
        db.session.commit()

    # Adding Tasks
    if not Tasks.query.filter_by(TaskName="Design DB tables").first():
        tasks = [
            Tasks(UserStoryID=1, TaskName="Design DB tables",
                  AssignedUserID=1, TaskStatus="Completed"),
            Tasks(UserStoryID=2, TaskName="Create login UI",
                  AssignedUserID=2, TaskStatus="In Progress"),
            Tasks(UserStoryID=2, TaskName="Develop login API",
                  AssignedUserID=2, TaskStatus="Not Started")
        ]
        db.session.add_all(tasks)
        db.session.commit()

    # Adding User Roles
    if not UserRoles.query.filter_by(UserID=1).first():
        user_roles = [
            UserRoles(UserID=1, RoleName="Developer"),
            UserRoles(UserID=2, RoleName="Developer"),
            UserRoles(UserID=3, RoleName="QA")
        ]
        db.session.add_all(user_roles)
        db.session.commit()

    print("Database populated successfully!")


@app.route('/')
def home():
    projects = ProjectDetails.query.all()
    for project in projects:
        print(f"Project: {project.ProjectName}, Owner: {project.product_owner.Name}")
    return render_template('index.html', projects=projects)


@app.route('/charts')
def charts():
    # Fetch data from the database
    sprints = SprintCalendar.query.all()
    projects = ProjectDetails.query.all()

    # Prepare data for the existing charts
    sprint_data = {
        "Days": [sprint.SprintNo for sprint in sprints],
        "Sprint Estimated Effort (Down)": [sprint.Velocity for sprint in sprints],
        "Sprint Actual Effort (Down)": [sprint.Velocity * 0.85 for sprint in sprints],
        "Sprint Estimated Effort (Up)": [sprint.Velocity for sprint in sprints],
        "Sprint Actual Effort (Up)": [sprint.Velocity * 0.95 for sprint in sprints]
    }

    data = pd.DataFrame(sprint_data)

    # Create a figure with 3 subplots arranged vertically
    fig, axes = plt.subplots(3, 1, figsize=(10, 18))

    # 1. Burn-Down Chart
    axes[0].plot(data['Days'], data['Sprint Estimated Effort (Down)'],
                 marker='o', linestyle='-', color='b', label='Estimated Effort')
    axes[0].plot(data['Days'], data['Sprint Actual Effort (Down)'],
                 marker='s', linestyle='--', color='r', label='Actual Effort')
    axes[0].set_title("Burn-Down Chart")
    axes[0].set_xlabel("Days")
    axes[0].set_ylabel("Effort Remaining")
    axes[0].legend()
    axes[0].grid(True)

    # 2. Burn-Up Chart
    axes[1].plot(data['Days'], data['Sprint Estimated Effort (Up)'],
                 marker='o', linestyle='-', color='g', label='Estimated Effort')
    axes[1].plot(data['Days'], data['Sprint Actual Effort (Up)'],
                 marker='s', linestyle='--', color='orange', label='Actual Effort')
    axes[1].set_title("Burn-Up Chart")
    axes[1].set_xlabel("Days")
    axes[1].set_ylabel("Effort Completed")
    axes[1].legend()
    axes[1].grid(True)

    # 3. Combined Chart (Both Up and Down)
    axes[2].plot(data['Days'], data['Sprint Estimated Effort (Down)'],
                 marker='o', linestyle='-', color='b', label='Estimated Effort (Down)')
    axes[2].plot(data['Days'], data['Sprint Actual Effort (Down)'],
                 marker='s', linestyle='--', color='r', label='Actual Effort (Down)')
    axes[2].plot(data['Days'], data['Sprint Estimated Effort (Up)'],
                 marker='o', linestyle='-', color='g', label='Estimated Effort (Up)')
    axes[2].plot(data['Days'], data['Sprint Actual Effort (Up)'],
                 marker='s', linestyle='--', color='orange', label='Actual Effort (Up)')
    axes[2].set_title("Combined Chart")
    axes[2].set_xlabel("Days")
    axes[2].set_ylabel("Effort")
    axes[2].legend()
    axes[2].grid(True)

    # Adjust spacing between subplots
    plt.tight_layout()

    # Save the figure to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # --- Donut Chart: Project Status Distribution ---
    status_counts = pd.Series([project.Status for project in projects]).value_counts()
    labels = status_counts.index
    sizes = status_counts.values
    colors = ["#4CAF50", "#FF9800", "#F44336"]  # Green, Orange, Red
    explode = (0.05, 0.05, 0.05)  # Slight separation for segments

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
           colors=colors, explode=explode, wedgeprops={'edgecolor': 'white'})

    # Add a circle for the donut shape
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    plt.title('Project Status Distribution')
    plt.tight_layout()

    # Save the figure to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    donut_chart_url = base64.b64encode(img.getvalue()).decode()

    # --- Velocity Chart: Sprint Velocities ---
    sprint_numbers = [s.SprintNo for s in sprints]
    velocities = [s.Velocity for s in sprints]
    print("Sprint Numbers:", sprint_numbers)
    print("Velocities:", velocities)

    plt.figure(figsize=(8, 6))
    plt.bar(sprint_numbers, velocities, color="#2196F3", edgecolor="black")

    plt.xlabel("Sprint Number")
    plt.ylabel("Velocity")
    plt.title("Sprint Velocity Chart")
    plt.xticks(sprint_numbers)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the figure to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    velocity_chart_url = base64.b64encode(img.getvalue()).decode()

    return render_template('charts.html', plot_url=plot_url, donut_chart_url=donut_chart_url, velocity_chart_url=velocity_chart_url)


if __name__ == '__main__':
    app.run(debug=True)