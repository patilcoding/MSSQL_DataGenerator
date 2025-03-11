import json
import os
import pyodbc
import random
import string
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from column_checker import generate_random_data  # Import column handling module

# ------------------ DATABASE CONNECTION ------------------
def load_credentials(file_path="credentials.txt"):
    """Read credentials from a text file and return them as a dictionary."""
    credentials = {}

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: Credentials file not found at {file_path}")
        return None

    # Read credentials
    with open(file_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                credentials[key] = value

    print("🔹 Loaded Credentials:", credentials)  # Debugging: See what’s loaded
    return credentials

# Load credentials from file
creds = load_credentials()
if creds is None:
    exit("⚠️ Exiting: No credentials found!")

# Fetch values with error handling
DB_SERVER = creds.get("DB_SERVER")
DB_DATABASE = creds.get("DB_DATABASE")
DB_USERNAME = creds.get("DB_USERNAME")
DB_PASSWORD = creds.get("DB_PASSWORD")

# Check for missing credentials
if not all([DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD]):
    print("❌ Error: One or more credentials are missing in credentials.txt!")
    exit(1)

# Database connection
try:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Error connecting to the database: {e}")

# ------------------ FETCH TABLE DETAILS ------------------
import datetime
import uuid
import re

def convert_sql_default(sql_default):
    """Convert SQL Server default values to Python-compatible values."""
    if sql_default is None:
        return None

    sql_default = sql_default.strip("()")  # Remove surrounding parentheses

    # Handle special SQL Server functions
    if sql_default.lower() == "getdate()":
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Convert to datetime
    elif sql_default.lower() == "newid()":
        return str(uuid.uuid4())  # Convert to UUID

    # Handle numeric and boolean values
    if re.match(r"^\d+(\.\d+)?$", sql_default):  # Check if it's a number
        return float(sql_default) if "." in sql_default else int(sql_default)

    return sql_default  # Return as string if no conversion is needed

def get_table_details(table_name):
    """Retrieve column details, primary keys, identity columns, and default values."""
    try:
        cursor.execute(f"""
            SELECT 
                c.COLUMN_NAME, 
                c.DATA_TYPE, 
                c.CHARACTER_MAXIMUM_LENGTH,
                COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') AS IsIdentity,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS c
            WHERE c.TABLE_NAME = '{table_name}'
        """)
        columns = []
        identity_columns = set()
        primary_keys = set()
        default_values = {}

        for row in cursor.fetchall():
            col_name, col_type, col_length, is_identity, col_default = row

            # Convert None to a usable default value
            col_length = col_length if col_length is not None else -1
            col_default = convert_sql_default(col_default)  # Convert SQL default to Python

            columns.append((col_name, col_type, col_length))

            if is_identity == 1:
                identity_columns.add(col_name)

            if col_default is not None:
                default_values[col_name] = col_default  # Store converted default values

        # Fetch primary keys
        cursor.execute(f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_NAME = '{table_name}' AND CONSTRAINT_NAME LIKE 'PK_%'
        """)
        for row in cursor.fetchall():
            primary_keys.add(row[0])

        return {
            "columns": columns,
            "primary_keys": primary_keys,
            "identity_columns": identity_columns,
            "default_values": default_values
        }

    except Exception as e:
        return {"error": str(e)}

    
# ------------------ GENERATE FAKE DATA FUNCTION ------------------
def generate_fake_data(table_name, num_records):
    """Generate unique fake data based on SQL Server table schema."""
    table_details = get_table_details(table_name)

    if "error" in table_details:
        return table_details  # Return the error instead of causing a crash

    print(f"🔍 DEBUG: Table Details for '{table_name}':", table_details)

    columns = table_details["columns"]
    identity_columns = table_details["identity_columns"]
    primary_keys = table_details["primary_keys"]
    default_values = table_details["default_values"]

    # ✅ Exclude TIMESTAMP Columns
    excluded_columns = {"RowVersionColumn"}  # Exclude TIMESTAMP from insertion
    valid_columns = [col for col in columns if col[0] not in excluded_columns]

    # Exclude problematic columns from insertion

    excluded_columns = {"RowVersionColumn", "BinaryColumn", "VarBinaryColumn", "ImageColumn", "SqlVariantColumn", "GeometryColumn", "GeographyColumn", "XmlColumn", "HierarchyIdColumn"}
    valid_columns = [col for col in columns if col[0] not in excluded_columns]

    generated_ids = set()
    generated_int_column = set()  # Store unique values for `IntColumn`

    data = []

    for _ in range(int(num_records)):
        row = []
        for column in valid_columns:
            col_name, col_type, col_length = column  # ✅ This will never fail now
            col_type = col_type.upper()

            # ✅ Ensure Identity Columns are set to None
            if col_name in identity_columns:
                row.append(None)  

            # ✅ Ensure Unique Primary Key for `IntColumn`
            elif col_name == "IntColumn":
                new_int_value = random.randint(100000, 999999)
                while new_int_value in generated_int_column:
                    new_int_value = random.randint(100000, 999999)
                generated_int_column.add(new_int_value)
                row.append(new_int_value)

            # ✅ Ensure Unique Primary Key for `ID`
            elif col_name in primary_keys:
                new_id = random.randint(100000, 999999)
                while new_id in generated_ids:
                    new_id = random.randint(100000, 999999)
                generated_ids.add(new_id)
                row.append(new_id)

            # ✅ Use DEFAULT values if available
            elif col_name in default_values:
                print(f"⚠️ USING DEFAULT for {col_name}: {default_values[col_name]}")
                row.append(default_values[col_name])

            else:
                value = generate_random_data(col_name, col_type, col_length)
                

                # ✅ Ensure NOT NULL columns always receive valid values
                if value is None:
                    print(f"⚠️ SKIPPING {col_name}: No valid value generated.")
                    continue

                row.append(value)

        data.append(tuple(row))

    return {"table": table_name, "generated_data": data}


# ------------------ HTTP SERVER HANDLER ------------------
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve the HTML page for the frontend."""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("C:/Users/Chirag/Downloads/Data Generator SSMS/HOSTED/index.html", "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle fake data generation and insertion into SQL Server."""
        if self.path == "/generate-data":
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = json.loads(self.rfile.read(content_length).decode("utf-8"))

                table_name = post_data.get("table_name")
                num_records = int(post_data.get("num_records", 10))

                table_details = get_table_details(table_name)

                if "error" in table_details:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(table_details).encode("utf-8"))
                    return

                fake_data = generate_fake_data(table_name, num_records)

                if "error" in fake_data:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(fake_data).encode("utf-8"))
                    return

                columns = [col[0] for col in table_details["columns"] if col[0] not in table_details["identity_columns"]]
                placeholders = ", ".join(["?" for _ in columns])
                column_names = ", ".join(columns)

                query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                batch_data = [
                    tuple(row[idx] for idx, col in enumerate(table_details["columns"]) if col[0] not in table_details["identity_columns"])
                    for row in fake_data["generated_data"]
                ]

                cursor.executemany(query, batch_data)
                conn.commit()

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": f"Inserted {num_records} records into {table_name}."}).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Internal Server Error", "details": str(e)}).encode("utf-8"))


# ------------------ RUN LOCAL SERVER ------------------
def run():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("🚀 Running server on http://localhost:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
