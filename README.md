# MSSQL_DataGenerator

Here’s a simple and user-friendly documentation for your project:  

---

# **MSSQL Data Generator**  

## **Overview**  
This project generates random test data for SQL Server databases. It allows users to populate their database with realistic data for testing and development purposes.  

## **Features**  
Generate random data using Python and Faker  
Supports multiple data types (UUID, dates, strings, etc.)  
Connects to SQL Server using `pyodbc`  
Runs as a simple HTTP server  

## **Requirements**  
- Python 3.x  
- SQL Server  
- Required Python packages (listed in `requirements.txt`)  

## **Installation & Setup**  

### **1. Clone the Repository**  
```sh
git clone https://github.com/patilcoding/MSSQL_DataGenerator.git
cd MSSQL_DataGenerator
```

### **2. Install Dependencies**  
```sh
pip install -r requirements.txt
```

### **3. Configure SQL Server Connection**  
Edit `credentials.txt` with your database credentials in the following format:  
```
server=your_server
database=your_database
username=your_username
password=your_password
```

### **4. Run the Server**  
```sh
python server.py
```
The server will start and listen for requests.

## **Usage**  
- Modify `column_checker.py` to define your own data generation rules.  
- Access the API or integrate it with your application.  

## **Upcoming Changes**
- making it available on docker
```
