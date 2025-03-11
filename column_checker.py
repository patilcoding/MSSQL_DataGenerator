import random
import string
import datetime
import uuid
from faker import Faker
import re
import os  

# Initialize Faker
fake = Faker()

def extract_size(col_type):
    """Extract size from VARCHAR or NVARCHAR data type."""
    match = re.search(r'\((\d+)\)', col_type)
    return int(match.group(1)) if match else None  

def generate_random_binary(size=10):
    """Generate random binary data for BINARY, VARBINARY, IMAGE columns."""
    return os.urandom(size)  # Generates random bytes

def generate_random_data(col_name, col_type, col_length=None):
    """Generate realistic fake data based on column names and types using Faker."""
    col_name_lower = col_name.lower()
    col_type = col_type.upper()

    # ✅ Always initialize `value`
    value = None  

    # ✅ Handle Numeric Data Types (Ensure correct values)
    if "TINYINT" in col_type:
        value = random.randint(0, 255)
    elif "SMALLINT" in col_type:
        value = random.randint(-32768, 32767)
    elif "INT" in col_type:
        value = random.randint(-2147483648, 2147483647)
    elif "BIGINT" in col_type:
        value = random.randint(-9223372036854775808, 9223372036854775807)
    elif "DECIMAL" in col_type or "NUMERIC" in col_type:
        value = round(random.uniform(1, 99999), 2)
    elif "FLOAT" in col_type or "REAL" in col_type:
        value = round(random.uniform(1, 1000), 6)
    elif "BIT" in col_type or "IS_" in col_name_lower:
        value = random.choice([0, 1])  # Ensure BIT columns store only 0 or 1

    # ✅ Handle Date & Time Data Types
    elif "DATE" in col_type or "DATETIME" in col_type:
        value = fake.date_time_this_decade().strftime("%Y-%m-%d %H:%M:%S")
    elif "TIME" in col_type:
        value = fake.time()
    elif "DATETIMEOFFSET" in col_type:
        value = fake.date_time().isoformat()

    # ✅ Handle String Data Types with Length Limits
    elif "VARCHAR" in col_type or "NVARCHAR" in col_type:
        max_length = col_length if col_length and col_length > 0 else 50  # Default max length
        value = fake.text(max_nb_chars=max_length)
    elif "CHAR" in col_type or "NCHAR" in col_type:
        value = fake.word()
    elif "TEXT" in col_type or "NTEXT" in col_type or "NVARCHAR(MAX)" in col_type:
        value = fake.paragraph(nb_sentences=3)

    # ✅ Handle Binary Data Types
    elif "BINARY" in col_type or "VARBINARY" in col_type or "IMAGE" in col_type:
        value = generate_random_binary(10)  # Generate 10 random bytes

    # ✅ Handle Special Data Types
    elif "UNIQUEIDENTIFIER" in col_type:
        value = str(uuid.uuid4())  # Generate random UUID
    elif "SQL_VARIANT" in col_type:
        value = random.choice(["text_value", 123, 45.67, fake.email()])  # Mixed data types
    elif "HIERARCHYID" in col_type:
        value = "/1/3/5/"  # Example hierarchy path
    elif "XML" in col_type:
        value = "<root><name>Example</name></root>"
    elif "GEOMETRY" in col_type:
        value = "POINT(-122.084 37.421998)"  # Example point (longitude, latitude)
    elif "GEOGRAPHY" in col_type:
        value = "POINT(-122.084 37.421998)"  # Example GPS location

    # ✅ Ensure value is never `None` before returning
    if value is None:
        print(f"⚠️ WARNING: Column {col_name} (Type: {col_type}) not recognized. Skipping...")
        return None  # ✅ Skip inserting this column instead of failing

    # ✅ Trim value to column max length if needed
    if col_length and col_length > 0 and isinstance(value, str):
        value = value[:col_length]  

    return value
