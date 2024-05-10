# models.py

# Import the necessary libraries
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Create a base class for the models
Base = declarative_base()

# Create the Employee class
class Employee(Base):
    __tablename__ = 'employees'

    emp_no = Column(Integer, primary_key=True)
    birth_date = Column(Date, nullable=False)
    first_name = Column(String(14), nullable=False)
    last_name = Column(String(16), nullable=False)
    gender = Column(Enum('M', 'F'), nullable=False)
    hire_date = Column(Date, nullable=False)

# Create a serialize method to return the object as a dictionary
    def serialize(self):
        return {
            'emp_no': self.emp_no,
            'birth_date': str(self.birth_date), 
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'hire_date': str(self.hire_date)  
        }
# Create the Department class
class Department(Base):
    __tablename__ = 'departments'

    dept_no = Column(String(4), primary_key=True)
    dept_name = Column(String(40), nullable=False)

# Create a serialize method to return the object as a dictionary
    def serialize(self):
        return {
            'dept_no': self.dept_no,
            'dept_name': self.dept_name
        }

# Create the Department Manager class
class DeptManager(Base):
    __tablename__ = 'dept_manager'

    emp_no = Column(Integer, ForeignKey('employees.emp_no'), primary_key=True)
    dept_no = Column(String(4), ForeignKey('departments.dept_no'), primary_key=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    employee = relationship('Employee')
    department = relationship('Department')

# Create a serialize method to return the object as a dictionary
    def serialize(self):
        return {
            'emp_no': self.emp_no,
            'dept_no': self.dept_no,
            'from_date': str(self.from_date),
            'to_date': str(self.to_date)
        }

# Create the Department Employee class
class DeptEmployee(Base):
    __tablename__ = 'dept_emp'

    emp_no = Column(Integer, ForeignKey('employees.emp_no'), primary_key=True)
    dept_no = Column(String(4), ForeignKey('departments.dept_no'), primary_key=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    employee = relationship('Employee')
    department = relationship('Department')

# Create a serialize method to return the object as a dictionary
    def serialize(self):
        return {
            'emp_no': self.emp_no,
            'dept_no': self.dept_no,
            'from_date': str(self.from_date),
            'to_date': str(self.to_date)
        }

# Create the Title class
class Title(Base):
    __tablename__ = 'titles'
    emp_no = Column(Integer, ForeignKey('employees.emp_no'), primary_key=True)
    title = Column(String(50), nullable=False)
    from_date = Column(Date, primary_key=True)  
    to_date = Column(Date, nullable=False)

# Create a serialize method to return the object as a dictionary
    def serialize(self):
        return {
            'emp_no': self.emp_no,
            'title': self.title,
            'from_date': str(self.from_date),
            'to_date': str(self.to_date)
        }
# Create the Salary class
class Salary(Base):
    __tablename__ = 'salaries'
    emp_no = Column(Integer, ForeignKey('employees.emp_no'), primary_key=True)
    salary = Column(Integer, nullable=False)
    from_date = Column(Date, primary_key=True)
    to_date = Column(Date, nullable=False)

# Create a serialize method to return the object as a dictionary
    def serialize(self):
        return {
            'emp_no': self.emp_no,
            'salary': self.salary,
            'from_date': str(self.from_date),
            'to_date': str(self.to_date)
        }

