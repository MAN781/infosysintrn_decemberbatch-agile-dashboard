import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def projects():
    # Connect to the SQLite database
    connection = sqlite3.connect("AgileProjectManagementDashboard.db")
    cursor = connection.cursor()

    # Query the ProjectDetails table
    query = """
    SELECT 
        pd."Project Name",
        po."Name",  -- Assuming the ProductOwner table has a 'Name' column for the project owner
        pd."Start Date",
        pd."End Date",
        pd."Revised End Date",
        pd."Status"
    FROM 
        ProjectDetails pd
    JOIN 
        ProductOwner po
    ON 
        pd."Product Owner Id" = po."Product Owner Id";
    """
    cursor.execute(query)
    projects_data = cursor.fetchall()

    # Query the total number of projects, active projects, and on hold projects
    cursor.execute("SELECT COUNT(*) FROM ProjectDetails WHERE Status = 'Active'")
    active_projects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ProjectDetails WHERE Status = 'On Hold'")
    on_hold_projects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ProjectDetails")
    total_projects = cursor.fetchone()[0]

    # Assuming that you want to display the first product owner's name
    cursor.execute("SELECT Name FROM Users WHERE Email = 'abhikr2210@gmail.com'")
    project_owner_name = cursor.fetchone()[0]

    # Close the database connection
    connection.close()

    # Map data into a list of dictionaries for easy use in the template
    projects = [
        {
            "project_name": row[0],
            "product_owner": row[1],
            "start_date": row[2],
            "end_date": row[3],
            "revised_end_date": row[4],
            "status": row[5]
        }
        for row in projects_data
    ]

    # Pass the project data and statistics to the template
    return render_template('sample.html', 
                           projects=projects, 
                           total_projects=total_projects, 
                           active_projects=active_projects, 
                           on_hold_projects=on_hold_projects,
                           project_owner_name=project_owner_name)


if __name__ == '__main__':
    app.run(debug=True)
