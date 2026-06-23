import sqlite3

conn = sqlite3.connect("judge.db")
cursor = conn.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# PROBLEMS
cursor.execute("""
CREATE TABLE IF NOT EXISTS problems(
    id INTEGER PRIMARY KEY,
    title TEXT,
    statement TEXT
)
""")

# SUBMISSIONS
cursor.execute("""
CREATE TABLE IF NOT EXISTS submissions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    problem_title TEXT,
    verdict TEXT,
    submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
INSERT OR IGNORE INTO problems
VALUES (1,'Sum of Two Numbers',
'Given two integers, print their sum.')
""")

cursor.execute("""
INSERT OR IGNORE INTO problems
VALUES (2,'Reverse String',
'Given a string, print its reverse.')
""")

cursor.execute("""
INSERT OR IGNORE INTO problems
VALUES (3,'Palindrome Check',
'Check whether a string is palindrome.')
""")

conn.commit()
conn.close()

print("Database Ready")