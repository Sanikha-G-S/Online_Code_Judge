import streamlit as st
import sqlite3
import tempfile
import subprocess

# -------------------------------
# SESSION STATE
# -------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------------------
# TITLE
# -------------------------------

st.title("Mini Online Judge")

# -------------------------------
# LOGIN / REGISTER
# -------------------------------

if not st.session_state.logged_in:

    st.header("Login / Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Register"):

            conn = sqlite3.connect("judge.db")
            cursor = conn.cursor()

            try:

                cursor.execute(
                    """
                    INSERT INTO users(username,password)
                    VALUES (?,?)
                    """,
                    (username, password)
                )

                conn.commit()

                st.success("Registration Successful")

            except:

                st.error("Username already exists")

            conn.close()

    with col2:

        if st.button("Login"):

            conn = sqlite3.connect("judge.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE username=?
                AND password=?
                """,
                (username, password)
            )

            user = cursor.fetchone()

            conn.close()

            if user:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:

                st.error("Invalid Credentials")

    st.stop()

# -------------------------------
# USER INFO
# -------------------------------

st.success(
    f"Logged in as: {st.session_state.username}"
)

if st.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()

# -------------------------------
# LOAD PROBLEMS
# -------------------------------

conn = sqlite3.connect("judge.db")
cursor = conn.cursor()

cursor.execute(
    """
    SELECT id,title
    FROM problems
    """
)

problems = cursor.fetchall()

conn.close()

# -------------------------------
# PROBLEM SELECTOR
# -------------------------------

selected_problem = st.selectbox(
    "Choose Problem",
    problems,
    format_func=lambda x: x[1]
)

problem_id = selected_problem[0]

# -------------------------------
# LOAD STATEMENT
# -------------------------------

conn = sqlite3.connect("judge.db")
cursor = conn.cursor()

cursor.execute(
    """
    SELECT statement
    FROM problems
    WHERE id=?
    """,
    (problem_id,)
)

statement = cursor.fetchone()[0]

conn.close()

st.header(selected_problem[1])

st.write(statement)

# -------------------------------
# SAMPLE IO
# -------------------------------

if problem_id == 1:

    st.code("""
Input:
2 3

Output:
5
""")

elif problem_id == 2:

    st.code("""
Input:
hello

Output:
olleh
""")

elif problem_id == 3:

    st.code("""
Input:
madam

Output:
YES
""")

# -------------------------------
# CODE EDITOR
# -------------------------------

code = st.text_area(
    "Write Python Code Here",
    height=300
)

# -------------------------------
# SUBMIT
# -------------------------------

if st.button("Submit Solution"):

    if code.strip() == "":

        st.warning("Please enter code.")

    else:

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".py",
                mode="w"
            ) as f:

                f.write(code)

                filename = f.name

            # -------------------------------
            # TEST CASES
            # -------------------------------

            if problem_id == 1:

                test_cases = [
                    ("2 3", "5"),
                    ("10 20", "30"),
                    ("100 200", "300")
                ]

            elif problem_id == 2:

                test_cases = [
                    ("hello", "olleh"),
                    ("python", "nohtyp"),
                    ("abc", "cba")
                ]

            elif problem_id == 3:

                test_cases = [
                    ("madam", "YES"),
                    ("racecar", "YES"),
                    ("hello", "NO")
                ]

            accepted = True

            # -------------------------------
            # RUN TEST CASES
            # -------------------------------

            for inp, expected in test_cases:

                result = subprocess.run(
                    ["python", filename],
                    input=inp,
                    text=True,
                    capture_output=True,
                    timeout=5
                )

                if result.stderr:

                    st.error("Runtime Error")

                    st.code(result.stderr)

                    accepted = False

                    break

                output = result.stdout.strip()

                if output != expected:

                    st.error("Wrong Answer")

                    st.write(f"Input: {inp}")
                    st.write(f"Expected Output: {expected}")
                    st.write(f"Your Output: {output}")

                    conn = sqlite3.connect("judge.db")
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO submissions
                        (username, problem_title, verdict)
                        VALUES (?, ?, ?)
                        """,
                        (
                            st.session_state.username,
                            selected_problem[1],
                            "Wrong Answer"
                        )
                    )

                    conn.commit()
                    conn.close()

                    accepted = False

                    break

            # -------------------------------
            # ACCEPTED
            # -------------------------------

            if accepted:

                st.success(
                    "✅ Accepted - All Test Cases Passed"
                )

                conn = sqlite3.connect("judge.db")
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO submissions
                    (username, problem_title, verdict)
                    VALUES (?, ?, ?)
                    """,
                    (
                        st.session_state.username,
                        selected_problem[1],
                        "Accepted"
                    )
                )

                conn.commit()
                conn.close()

        except subprocess.TimeoutExpired:

            st.error("⏰ Time Limit Exceeded")

        except Exception as e:

            st.error(str(e))

# -------------------------------
# DASHBOARD
# -------------------------------

st.header("📊 Dashboard")

conn = sqlite3.connect("judge.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM submissions"
)

total = cursor.fetchone()[0]

cursor.execute(
    """
    SELECT COUNT(*)
    FROM submissions
    WHERE verdict='Accepted'
    """
)

accepted_count = cursor.fetchone()[0]

wrong_count = total - accepted_count

success_rate = 0

if total > 0:
    success_rate = round(
        accepted_count * 100 / total,
        2
    )

conn.close()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total", total)
c2.metric("Accepted", accepted_count)
c3.metric("Wrong", wrong_count)
c4.metric("Success %", success_rate)

# -------------------------------
# SUBMISSION HISTORY
# -------------------------------

st.header("📜 Recent Submissions")

conn = sqlite3.connect("judge.db")
cursor = conn.cursor()

cursor.execute(
    """
    SELECT
    username,
    problem_title,
    verdict,
    submission_time
    FROM submissions
    ORDER BY id DESC
    LIMIT 10
    """
)

rows = cursor.fetchall()

conn.close()

for row in rows:

    st.write(
        f"{row[0]} | {row[1]} | {row[2]} | {row[3]}"
    )

# -------------------------------
# LEADERBOARD
# -------------------------------

st.header("🏆 Leaderboard")

conn = sqlite3.connect("judge.db")
cursor = conn.cursor()

cursor.execute(
    """
    SELECT
    username,
    COUNT(*)
    FROM submissions
    WHERE verdict='Accepted'
    GROUP BY username
    ORDER BY COUNT(*) DESC
    """
)

leaders = cursor.fetchall()

conn.close()

rank = 1

for row in leaders:

    st.write(
        f"{rank}. {row[0]} - {row[1]} solved"
    )

    rank += 1