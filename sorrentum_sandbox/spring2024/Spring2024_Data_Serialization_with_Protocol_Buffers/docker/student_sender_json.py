import time
import socket
import random
import string
import json
from dataclasses import asdict, dataclass
from typing import List, Optional

@dataclass
class Name:
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

@dataclass
class Student:
    user_id: int
    username: str
    emails: List[str]
    graduated: bool
    gender: str
    name: Name
    degree_type: str

class StudentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Student):
            return asdict(obj)
        elif isinstance(obj, Name):
            return asdict(obj)
        return super().default(obj)

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8888

def generate_random_student():
    user_id = random.randint(1000, 9999)
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    num_emails = random.randint(1, 3)
    emails = [f"{username}@example.{random.choice(['com', 'org', 'net'])}" for _ in range(num_emails)]
    graduated = random.choice([True, False])
    gender = random.choice(['Male', 'Female'])
    first_name = ''.join(random.choices(string.ascii_letters, k=random.randint(3, 8)))
    last_name = ''.join(random.choices(string.ascii_letters, k=random.randint(3, 10)))
    middle_name = ''.join(random.choices(string.ascii_letters, k=random.randint(3, 8))) if random.choice([True, False]) else None
    degree_type = random.choice(['Bachelor', 'Master', 'Doctor'])

    student = Student(
        user_id=user_id,
        username=username,
        emails=emails,
        graduated=graduated,
        gender=gender,
        name=Name(first_name=first_name, last_name=last_name, middle_name=middle_name),
        degree_type=degree_type
    )

    return student

def send_students(num_students=1000):
    students = [generate_random_student() for _ in range(num_students)]

    start_time = time.time()
    serialized_students = json.dumps(students, cls=StudentEncoder)
    end_time = time.time()

    serialization_time = (end_time - start_time) * (1e6)
    total_bytes = len(serialized_students)

    print(f"Serialize {num_students} students in {serialization_time:.2f} microseconds")
    print(f"Average serialization time per student: {serialization_time / num_students:.2f} microseconds")
    print(f"Total Serialization Size: {total_bytes} bytes")
    print(f"Average bytes per student: {total_bytes / num_students:.2f} bytes")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    client_socket.sendall(serialized_students.encode())
    client_socket.close()

if __name__ == "__main__":
    random.seed(0)
    send_students(num_students=10000)
