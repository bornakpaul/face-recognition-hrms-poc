import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5434",
    database="hrms",
    user="admin",
    password="admin"
)

cursor = conn.cursor()