# Import required libraries
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Employee, Department, DeptEmployee, DeptManager, Title, Salary

# Create a Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'


# Create a SQLAlchemy engine
db_uri = 'mysql://root:password@mysql:3306/employees'
engine = create_engine(db_uri)

# Create a SQLAlchemy session
Session = sessionmaker(bind=engine)
session = Session()
#----------------Authentication-----------------#
# Initialize JWTManager
jwt = JWTManager(app)
users = {
    "username": "password"
}

# Token-based authentication endpoint
@app.route('/auth', methods=['POST'])
def authenticate():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Check if the username and password are valid
    if username in users and users[username] == password:
        # Generate JWT token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Protected endpoint that requires a valid JWT token
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Access identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# Routes for CRUD operations
# ---------------Create Operations----------------#

# Create a new employee
@app.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    # Parse request data
    data = request.json
    # Create a new Employee instance
    new_employee = Employee(
        emp_no=data['emp_no'],
        birth_date=data['birth_date'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        gender=data['gender'],
        hire_date=data['hire_date']
    )

    # Add the new employee to the session
    session.add(new_employee)

    try:
        # Commit the changes to persist the new employee in the database
        session.commit()
        return jsonify({'message': 'Employee created successfully'}), 201
    except Exception as e:
        # Rollback the session in case of any error
        session.rollback()
        return jsonify({'error': str(e)}), 500

# Create Employee Title
@app.route('/titles', methods=['POST'])
@jwt_required()
def create_title():
    # Parse request data
    data = request.json

    # Create a new Title instance
    new_title = Title(
        emp_no=data['emp_no'],
        title=data['title'],
        from_date=data['from_date'],
        to_date=data['to_date']
    )

    # Add the new title to the session
    session.add(new_title)

    try:
        # Commit the changes to persist the new title in the database
        session.commit()
        # Return the created title data
        return jsonify({'message': 'Title created successfully'}), 201
    except Exception as e:
        # Rollback the session in case of any error
        session.rollback()
        return jsonify({'error': str(e)}), 500

# Create Employee Salary
@app.route('/salaries', methods=['POST'])
@jwt_required()
def create_salary():
    # Parse request data
    data = request.json

    # Create a new Salary instance
    new_salary = Salary(
        emp_no=data['emp_no'],
        salary=data['salary'],
        from_date=data['from_date'],
        to_date=data['to_date']
    )

    # Add the new salary to the session
    session.add(new_salary)

    try:
        # Commit the changes to persist the new salary in the database
        session.commit()
        # Return the created salary data
        return jsonify({'message': 'Salary created successfully'}), 201
    except Exception as e:
        # Rollback the session in case of any error
        session.rollback()
        return jsonify({'error': str(e)}), 500

# Employee Department Assignment
@app.route('/dept_employees', methods=['POST'])
@jwt_required()
def assign_department():
    # Parse request data
    data = request.json

    # Create a new DeptEmployee instance
    new_dept_employee = DeptEmployee(
        emp_no=data['emp_no'],
        dept_no=data['dept_no'],
        from_date=data['from_date'],
        to_date=data['to_date']
    )

    # Add the new department employee record to the session
    session.add(new_dept_employee)

    try:
        # Commit the changes to persist the new department employee record in the database
        session.commit()
        # Return the created department employee record data
        return jsonify({'message': 'Department employee record created successfully'}), 201
    except Exception as e:
        # Rollback the session in case of any error
        session.rollback()
        return jsonify({'error': str(e)}), 500

# Create New Department
@app.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    # Parse request data
    data = request.json

    # Create a new Department instance
    new_department = Department(
        dept_no=data['dept_no'],
        dept_name=data['dept_name']
    )

    # Add the new department to the session
    session.add(new_department)

    try:
        # Commit the changes to persist the new department in the database
        session.commit()
        # Return the created department data
        return jsonify({'message': 'Department created successfully'}), 201
    except Exception as e:
        # Rollback the session in case of any error
        session.rollback()
        return jsonify({'error': str(e)}), 500
    
# Assign Department Manager
@app.route('/dept_managers', methods=['POST'])
@jwt_required()
def assign_department_manager():
    # Parse request data
    data = request.json

    # Create a new DeptManager instance
    new_dept_manager = DeptManager(
        emp_no=data['emp_no'],
        dept_no=data['dept_no'],
        from_date=data['from_date'],
        to_date=data['to_date']
    )

    # Add the new department manager record to the session
    session.add(new_dept_manager)

    try:
        # Commit the changes to persist the new department manager record in the database
        session.commit()
        # Return the created department manager record data
        return jsonify({'message': 'Department manager record created successfully'}), 201
    except Exception as e:
        # Rollback the session in case of any error
        session.rollback()
        return jsonify({'error': str(e)}), 500


#-----------Read Operations----------------#

# Get All Employees
@app.route('/employees', methods=['GET'])
def get_employees():
    # Query all employees using SQLAlchemy
    employees = session.query(Employee).all()

    # Serialize the employees' data
    serialized_employees = []
    for employee in employees:
        serialized_employee = {
            'emp_no': employee.emp_no,
            'birth_date': employee.birth_date,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'gender': employee.gender,
            'hire_date': employee.hire_date
        }
        serialized_employees.append(serialized_employee)

    # Return the JSON response containing the employees' data
    return jsonify(serialized_employees)

    # Return the JSON response containing the employees' data
    return jsonify(serialized_employees)
# Search Employee by ID
@app.route('/employees/<int:emp_no>', methods=['GET'])
def get_employee(emp_no):
    employee = session.query(Employee).filter_by(emp_no=emp_no).first()
    if employee:
        return jsonify(employee.serialize())
    else:
        return jsonify({'error': 'Employee not found'}), 404


# Search employees by name
@app.route('/employees/search', methods=['GET'])
def search_employees():
    keyword = request.args.get('keyword')
    employees = session.query(Employee).filter(Employee.first_name.ilike(f'%{keyword}%') |
                                               Employee.last_name.ilike(f'%{keyword}%')).all()
    return jsonify([employee.serialize() for employee in employees])

# Aggregation - Total number of employees
@app.route('/employees/total', methods=['GET'])
def total_employees():
    total_count = session.query(Employee).count()
    return jsonify({'total_employees': total_count})


# View Titles Table Endpoint
@app.route('/titles', methods=['GET'])
def view_titles():
    titles = session.query(Title).all()
    return jsonify([title.serialize() for title in titles])

# View Titles by Employee ID Endpoint
@app.route('/titles/<int:emp_no>', methods=['GET'])
def view_titles_by_emp_no(emp_no):
    titles = session.query(Title).filter_by(emp_no=emp_no).all()
    return jsonify([title.serialize() for title in titles])


# View Salaries Table Endpoint
@app.route('/salaries', methods=['GET'])
def view_salaries():
    salaries = session.query(Salary).all()
    return jsonify([salary.serialize() for salary in salaries])

# View Department Employees Table Endpoint
@app.route('/dept_employees', methods=['GET'])
def view_department_employees():
    department_employees = session.query(DeptEmployee).all()
    return jsonify([dept_employee.serialize() for dept_employee in department_employees])

# View Department Employees by Employee ID Endpoint
@app.route('/dept_employees/<int:emp_no>', methods=['GET'])
def view_department_employees_by_emp_no(emp_no):
    department_employees = session.query(DeptEmployee).filter_by(emp_no=emp_no).all()
    return jsonify([dept_employee.serialize() for dept_employee in department_employees])

# View Departments Table Endpoint
@app.route('/departments', methods=['GET'])
def view_departments():
    departments = session.query(Department).all()
    return jsonify([department.serialize() for department in departments])

# View Department Managers Table Endpoint
@app.route('/dept_managers', methods=['GET'])
def view_department_managers():
    department_managers = session.query(DeptManager).all()
    return jsonify([dept_manager.serialize() for dept_manager in department_managers])


#------------Update Operations----------------#

# Update Employee Information Endpoint
@app.route('/employees/<int:emp_no>', methods=['PUT'])
@jwt_required()
def update_employee(emp_no):
    # Parse request data
    data = request.json
    new_first_name = data.get('first_name')
    new_last_name = data.get('last_name')
    new_gender = data.get('gender')
    new_hire_date = data.get('hire_date')

    # Create a session
    session = Session()

    try:
        # Retrieve the employee from the database
        employee = session.query(Employee).filter_by(emp_no=emp_no).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Update employee information
        if new_first_name:
            employee.first_name = new_first_name
        if new_last_name:
            employee.last_name = new_last_name
        if new_gender:
            employee.gender = new_gender
        if new_hire_date:
            employee.hire_date = new_hire_date

        # Commit the changes to the database
        session.commit()

        # Return the updated employee data
        return jsonify(employee.serialize())
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()

# Update Titles Table Endpoint
@app.route('/titles/<int:emp_no>', methods=['PUT'])
@jwt_required()
def update_titles(emp_no):
    # Parse request data
    data = request.json
    new_title = data.get('title')
    new_from_date = data.get('from_date')
    new_to_date = data.get('to_date')

    # Create a session
    session = Session()

    try:
        # Retrieve the title records from the database
        titles = session.query(Title).filter_by(emp_no=emp_no).all()
        if not titles:
            return jsonify({'error': 'No titles found for employee'}), 404

        # Update title information
        if new_title:
            for title in titles:
                title.title = new_title
        if new_from_date:
            for title in titles:
                title.from_date = new_from_date
        if new_to_date:
            for title in titles:
                title.to_date = new_to_date

        # Commit the changes to the database
        session.commit()

        # Return the updated title records data
        return jsonify([title.serialize() for title in titles])
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()

# Update Managerial Assignment Endpoint
@app.route('/employees/<int:emp_no>/managerial_assignment', methods=['PUT'])
@jwt_required()
def update_managerial_assignment(emp_no):
    # Parse request data
    data = request.json
    new_dept_no = data.get('dept_no')
    new_from_date = data.get('from_date')
    new_to_date = data.get('to_date')

    # Create a session
    session = Session()

    try:
        # Retrieve the managerial assignment record from the database
        managerial_assignment_record = session.query(DeptManager).filter_by(emp_no=emp_no).first()
        if not managerial_assignment_record:
            return jsonify({'error': 'Managerial assignment record not found'}), 404

        # Update managerial assignment information
        if new_dept_no:
            managerial_assignment_record.dept_no = new_dept_no
        if new_from_date:
            managerial_assignment_record.from_date = new_from_date
        if new_to_date:
            managerial_assignment_record.to_date = new_to_date

        # Commit the changes to the database
        session.commit()

        # Return the updated managerial assignment record data
        return jsonify(managerial_assignment_record.serialize())
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()


# Update Department Information Endpoint
@app.route('/departments/<string:dept_no>', methods=['PUT'])
@jwt_required()
def update_department(dept_no):
    # Parse request data
    data = request.json
    new_dept_name = data.get('dept_name')

    # Create a session
    session = Session()

    try:
        # Retrieve the department record from the database
        department = session.query(Department).filter_by(dept_no=dept_no).first()
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        # Update department information
        if new_dept_name:
            department.dept_name = new_dept_name

            # Commit the changes to the database
            session.commit()

            # Return the updated department record data
            return jsonify(department.serialize())
        else:
            return jsonify({'error': 'New department name is required'}), 400
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()

# Modify Title Names Endpoint
@app.route('/titles/<int:emp_no>', methods=['PUT'])
@jwt_required()
def modify_title_names(emp_no):
    # Parse request data
    data = request.json
    new_title = data.get('title')

    # Create a session
    session = Session()

    try:
        # Retrieve the title records from the database
        titles = session.query(Title).filter_by(emp_no=emp_no).all()
        if not titles:
            return jsonify({'error': 'No titles found for employee'}), 404

        # Update title names
        if new_title:
            for title in titles:
                title.title = new_title

            # Commit the changes to the database
            session.commit()

            # Return the updated title records data
            return jsonify([title.serialize() for title in titles])
        else:
            return jsonify({'error': 'New title is required'}), 400
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()

# Adjust Salary Ranges Endpoint
@app.route('/salaries/<int:emp_no>', methods=['PUT'])
@jwt_required()
def adjust_salary_ranges(emp_no):
    # Parse request data
    data = request.json
    new_salary = data.get('salary')

    # Create a session
    session = Session()

    try:
        # Retrieve the salary records from the database
        salaries = session.query(Salary).filter_by(emp_no=emp_no).all()
        if not salaries:
            return jsonify({'error': 'No salaries found for employee'}), 404

        # Adjust salary ranges
        if new_salary:
            for salary in salaries:
                salary.salary = new_salary

            # Commit the changes to the database
            session.commit()

            # Return the adjusted salary records data
            return jsonify([salary.serialize() for salary in salaries])
        else:
            return jsonify({'error': 'New salary is required'}), 400
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()

# Update Department Employee Endpoint
@app.route('/dept_employees/<int:emp_no>', methods=['PUT'])
@jwt_required()
def update_department_employee(emp_no):
    # Parse request data
    data = request.json
    new_dept_no = data.get('dept_no')
    new_from_date = data.get('from_date')
    new_to_date = data.get('to_date')

    # Create a session
    session = Session()

    try:
        # Retrieve the department employee record from the database
        dept_employee = session.query(DeptEmployee).filter_by(emp_no=emp_no).first()
        if not dept_employee:
            return jsonify({'error': 'Department employee not found'}), 404

        # Update department employee information
        if new_dept_no:
            dept_employee.dept_no = new_dept_no
        if new_from_date:
            dept_employee.from_date = new_from_date
        if new_to_date:
            dept_employee.to_date = new_to_date

        # Commit the changes to the database
        session.commit()

        # Return the updated department employee record data
        return jsonify(dept_employee.serialize())
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()

# Update Department Manager Endpoint
@app.route('/dept_managers/<int:emp_no>', methods=['PUT'])
@jwt_required()
def update_department_manager(emp_no):
    # Parse request data
    data = request.json
    new_dept_no = data.get('dept_no')
    new_from_date = data.get('from_date')
    new_to_date = data.get('to_date')

    # Create a session
    session = Session()

    try:
        # Retrieve the department manager record from the database
        dept_manager = session.query(DeptManager).filter_by(emp_no=emp_no).first()
        if not dept_manager:
            return jsonify({'error': 'Department manager not found'}), 404

        # Update department manager information
        if new_dept_no:
            dept_manager.dept_no = new_dept_no
        if new_from_date:
            dept_manager.from_date = new_from_date
        if new_to_date:
            dept_manager.to_date = new_to_date

        # Commit the changes to the database
        session.commit()

        # Return the updated department manager record data
        return jsonify(dept_manager.serialize())
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()


#------------Delete Operations----------------#

# Delete Employee Endpoint
@app.route('/employees/<int:emp_no>', methods=['DELETE'])
@jwt_required()
def delete_employee(emp_no):
    # Create a session
    session = Session()

    try:
        # Retrieve the employee record to be deleted
        employee = session.query(Employee).filter_by(emp_no=emp_no).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Delete the employee record
        session.delete(employee)

        # Commit the changes to the database
        session.commit()

        return jsonify({'message': 'Employee deleted successfully'})
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()

# Delete Batch Employees Endpoint
@app.route('/employees/delete_batch', methods=['DELETE'])
@jwt_required()
def delete_batch_employees():
    # Parse request data
    data = request.json
    emp_nos = data.get('emp_nos')

    # Create a session
    session = Session()

    try:
        # Retrieve the employee records to be deleted
        employees = session.query(Employee).filter(Employee.emp_no.in_(emp_nos)).all()

        # Delete the employee records
        for employee in employees:
            session.delete(employee)

        # Commit the changes to the database
        session.commit()

        return jsonify({'message': 'Employees deleted successfully'})
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()
# Delete Department
@app.route('/departments/<string:dept_no>', methods=['DELETE'])
@jwt_required()
def delete_department(dept_no):
    # Create a session
    session = Session()

    try:
        # Retrieve the department record to be deleted
        department = session.query(Department).filter_by(dept_no=dept_no).first()
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        # Delete the department record
        session.delete(department)

        # Commit the changes to the database
        session.commit()

        return jsonify({'message': 'Department deleted successfully'})
    except Exception as e:
        # Rollback the transaction if an error occurs
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)