from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------- DATABASE CONNECTION ----------------------
def get_connection():
    # NOTE: adjust credentials if different on your machine
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nusrat@80",
        database="police",
        buffered=True
    )

# ---------------------- HELPERS ----------------------
def to_int_or_none(v):
    try:
        return int(v) if v not in (None, "", "None") else None
    except Exception:
        return None

def to_float_or_none(v):
    try:
        return float(v) if v not in (None, "", "None") else None
    except Exception:
        return None

def to_none_if_empty(v):
    return v if (v is not None and str(v).strip() != "") else None

@app.template_filter("ymd")
def ymd(value):
    """Format a date/datetime/str to YYYY-MM-DD for <input type=date>."""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    if value is None:
        return ""
    # best effort if it's a string like '2025-11-01 00:00:00'
    s = str(value)
    return s[:10]  # 'YYYY-MM-DD'

# ====================== HOME / INDEX ======================
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_cases FROM CaseTable;")
    total_cases = cursor.fetchone()['total_cases']

    cursor.execute("SELECT COUNT(*) AS total_police FROM Police;")
    total_police = cursor.fetchone()['total_police']

    try:
        cursor.execute("SELECT COUNT(*) AS total_criminals FROM Criminal;")
        total_criminals = cursor.fetchone()['total_criminals']
    except Exception:
        total_criminals = 0

    try:
        cursor.execute("SELECT COUNT(*) AS total_departments FROM Department;")
        total_departments = cursor.fetchone()['total_departments']
    except Exception:
        total_departments = 0

    cursor.execute("""
        SELECT 
            c.CaseID, 
            c.CaseType, 
            c.Stage,
            p.PoliceName AS Officer
        FROM CaseTable c
        LEFT JOIN Police p ON c.AssignedOfficer_ID = p.PoliceID
        ORDER BY c.DateReported DESC
        LIMIT 5;
    """)
    recent_cases = cursor.fetchall()

    conn.close()
    return render_template('index.html',
                           total_cases=total_cases,
                           total_police=total_police,
                           total_criminals=total_criminals,
                           total_departments=total_departments,
                           recent_cases=recent_cases)

# ====================== OFFICERS ======================
@app.route('/officers')
def officers_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    dept_id = request.args.get('dept_id', '').strip()
    dept_type = request.args.get('dept_type', '').strip()
    dept_head = request.args.get('dept_head', '').strip()

    query = """
        SELECT 
            p.PoliceID,
            p.PoliceName,
            p.Ranking,
            p.Email,
            p.PhoneNumber,
            p.Salary,
            p.Age,
            p.Date_of_Birth,
            p.Dept_ID,
            d.DepartmentType AS DepartmentName,
            (
                SELECT COUNT(*) 
                FROM CaseTable c 
                WHERE c.AssignedOfficer_ID = p.PoliceID
            ) AS CaseCount
        FROM Police p
        LEFT JOIN Department d ON p.Dept_ID = d.Dept_ID
        WHERE 1=1
    """

    params = []

    if dept_id:
        query += " AND p.Dept_ID = %s"
        params.append(dept_id)
    if dept_type:
        query += " AND d.DepartmentType LIKE %s"
        params.append(f"%{dept_type}%")
    if dept_head:
        query += " AND p.Dept_ID IN (SELECT Dept_ID FROM Department WHERE DepartmentHead LIKE %s)"
        params.append(f"%{dept_head}%")

    query += " ORDER BY p.PoliceName;"
    cursor.execute(query, params)
    officers = cursor.fetchall()

    # 🔥 THIS WAS MISSING — required for View Cases modal
    cursor.execute("""
        SELECT 
            CaseID,
            CaseType,
            Stage,
            Verdict,
            ProgressPercentage,
            AssignedOfficer_ID
        FROM CaseTable;
    """)
    all_cases = cursor.fetchall()

    cursor.execute("SELECT Dept_ID, DepartmentType FROM Department;")
    departments = cursor.fetchall()

    conn.close()
    return render_template('officers.html',
                           officers=officers,
                           departments=departments,
                           all_cases=all_cases)

@app.route('/add_officer', methods=['GET', 'POST'])
def add_officer():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        rank = request.form['rank']
        email = request.form['email']
        phone = request.form['phone']
        dept_id = to_int_or_none(request.form.get('dept'))
        salary = to_float_or_none(request.form.get('salary'))
        age = to_int_or_none(request.form.get('age'))
        dob = to_none_if_empty(request.form.get('dob'))

        if age is None or age < 18 or age > 55:
            flash("⛔ Age must be between 18 and 55", "error")
            conn.close()
            return redirect(url_for('add_officer'))

        try:
            cursor.execute("""
                INSERT INTO Police (PoliceName, Ranking, Email, PhoneNumber, Dept_ID, Salary, Age, Date_of_Birth)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (name, rank, email, phone, dept_id, salary, age, dob))
            conn.commit()
            flash("✅ Officer added successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error: {e}", "error")
        conn.close()
        return redirect(url_for('officers_page'))

    cursor.execute("SELECT Dept_ID, DepartmentType FROM Department;")
    departments = cursor.fetchall()
    conn.close()
    return render_template('add_officer.html', departments=departments)

@app.route('/edit_officer/<int:police_id>', methods=['POST'])
def edit_officer(police_id):
    conn = get_connection()
    cursor = conn.cursor()
    name = request.form.get('name')
    rank = request.form.get('rank')
    email = request.form.get('email')
    phone = request.form.get('phone')
    age = to_int_or_none(request.form.get('age'))
    salary = to_float_or_none(request.form.get('salary'))
    dept_id = to_int_or_none(request.form.get('dept_id'))
    dob = to_none_if_empty(request.form.get('dob'))

    try:
        if age is None or age < 18 or age > 55:
            flash("⛔ Age must be between 18 and 55", "error")
            conn.close()
            return redirect(url_for('officers_page'))

        cursor.execute("""
            UPDATE Police
               SET PoliceName=%s, Ranking=%s, Email=%s, PhoneNumber=%s,
                   Age=%s, Salary=%s, Dept_ID=%s, Date_of_Birth=%s
             WHERE PoliceID=%s
        """, (name, rank, email, phone, age, salary, dept_id, dob, police_id))
        conn.commit()
        flash("✅ Officer updated successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"⛔ Error updating officer: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('officers_page'))

@app.route('/delete_officer/<int:police_id>', methods=['POST'])
def delete_officer(police_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # clear FKs first
        cursor.execute("UPDATE CaseTable SET AssignedOfficer_ID=NULL WHERE AssignedOfficer_ID=%s", (police_id,))
        cursor.execute("UPDATE CourtProceedings SET PoliceID=NULL WHERE PoliceID=%s", (police_id,))
        # now delete officer
        cursor.execute("DELETE FROM Police WHERE PoliceID=%s", (police_id,))
        conn.commit()
        flash("🗑️ Officer deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"⛔ Error deleting officer: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('officers_page'))

# ====================== CASES ======================
@app.route('/cases')
def cases_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    case_type = request.args.get('type', '').strip()
    officer_name = request.args.get('officer', '').strip()
    verdict = request.args.get('verdict', '').strip()

    query = """
        SELECT 
            c.CaseID,
            c.CaseType,
            c.DateReported,
            c.Description_Of_Case,
            c.ProgressPercentage,
            c.Verdict,
            c.Stage,
            c.AssignedOfficer_ID,
            p.PoliceName AS AssignedOfficer,
            p.Ranking AS OfficerRank,
            d.DepartmentType AS OfficerDepartment
        FROM CaseTable c
        LEFT JOIN Police p ON c.AssignedOfficer_ID = p.PoliceID
        LEFT JOIN Department d ON p.Dept_ID = d.Dept_ID
        WHERE 1=1
    """
    params = []
    if case_type:
        query += " AND c.CaseType LIKE %s"
        params.append(f"%{case_type}%")
    if officer_name:
        query += " AND p.PoliceName LIKE %s"
        params.append(f"%{officer_name}%")
    if verdict:
        query += " AND c.Verdict LIKE %s"
        params.append(f"%{verdict}%")
    query += " ORDER BY c.DateReported DESC;"

    cursor.execute(query, params)
    cases = cursor.fetchall()
    conn.close()
    return render_template('cases.html', cases=cases)

@app.route('/add_case', methods=['GET', 'POST'])
def add_case():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        case_type = request.form['case_type']
        description = request.form['description']
        date_reported = request.form['date_reported']
        progress = to_float_or_none(request.form['progress'])
        verdict = request.form['verdict']
        stage = request.form['stage']
        assigned_officer = to_int_or_none(request.form.get('assigned_officer'))

        try:
            cursor.execute("""
                INSERT INTO CaseTable 
                (CaseType, Description_Of_Case, DateReported, ProgressPercentage, Verdict, Stage, AssignedOfficer_ID)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (case_type, description, date_reported, progress, verdict, stage, assigned_officer))
            conn.commit()
            flash("✅ Case added successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error adding case: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('cases_page'))

    cursor.execute("SELECT PoliceID, PoliceName FROM Police;")
    officers = cursor.fetchall()
    conn.close()
    return render_template('add_case.html', officers=officers)

@app.route('/edit_case/<int:case_id>', methods=['GET', 'POST'])
def edit_case(case_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        case_type = request.form['case_type']
        description = request.form['description']
        date_reported = request.form['date_reported']
        progress = to_float_or_none(request.form['progress'])
        verdict = request.form['verdict']
        stage = request.form['stage']
        assigned_officer = to_int_or_none(request.form.get('assigned_officer'))
        try:
            cursor.execute("""
                UPDATE CaseTable
                SET CaseType=%s, Description_Of_Case=%s, DateReported=%s, 
                    ProgressPercentage=%s, Verdict=%s, Stage=%s, AssignedOfficer_ID=%s
                WHERE CaseID=%s
            """, (case_type, description, date_reported, progress, verdict, stage, assigned_officer, case_id))
            conn.commit()
            flash("✅ Case updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error updating case: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('cases_page'))

    cursor.execute("SELECT * FROM CaseTable WHERE CaseID = %s", (case_id,))
    case = cursor.fetchone()
    cursor.execute("SELECT PoliceID, PoliceName FROM Police;")
    officers = cursor.fetchall()
    conn.close()
    return render_template('edit_case.html', case=case, officers=officers)

@app.route('/delete_case/<int:case_id>', methods=['POST'])
def delete_case(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # clear dependents in correct order
        cursor.execute("UPDATE Criminal SET CaseID=NULL WHERE CaseID=%s", (case_id,))
        cursor.execute("DELETE FROM CourtProceedings WHERE CaseID=%s", (case_id,))
        cursor.execute("DELETE FROM Evidence WHERE CaseID=%s", (case_id,))
        cursor.execute("DELETE FROM CaseTable WHERE CaseID=%s", (case_id,))
        conn.commit()
        flash("🗑️ Case deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"⛔ Error deleting case: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('cases_page'))

# ====================== CRIMINALS ======================
@app.route('/criminals')
def criminals_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    name = request.args.get('name', '').strip()
    gender = request.args.get('gender', '').strip()
    case_id = request.args.get('case', '').strip()

    cursor.execute("SELECT COUNT(*) AS total FROM Criminal;")
    total_criminals = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) AS male FROM Criminal WHERE Gender='M';")
    male = cursor.fetchone()['male']
    cursor.execute("SELECT COUNT(*) AS female FROM Criminal WHERE Gender='F';")
    female = cursor.fetchone()['female']
    cursor.execute("SELECT ROUND(AVG(Age), 1) AS avg_age FROM Criminal;")
    avg_age = cursor.fetchone()['avg_age']

    query = """
        SELECT 
            c.Criminal_ID,
            c.Name_,
            c.Address,
            c.DateofBirth,
            c.Gender,
            c.CriminalRecord,
            c.Age,
            c.TrialDuration,
            t.CaseType
        FROM Criminal c
        LEFT JOIN CaseTable t ON c.CaseID = t.CaseID
        WHERE 1=1
    """
    params = []
    if name:
        query += " AND c.Name_ LIKE %s"; params.append(f"%{name}%")
    if gender:
        query += " AND c.Gender = %s"; params.append(gender)
    if case_id:
        query += " AND c.CaseID = %s"; params.append(case_id)
    query += " ORDER BY c.Name_ ASC;"
    cursor.execute(query, params)
    criminals = cursor.fetchall()

    conn.close()
    return render_template('criminals.html',
                           criminals=criminals,
                           total_criminals=total_criminals,
                           male=male,
                           female=female,
                           avg_age=avg_age)

@app.route('/add_criminal', methods=['GET', 'POST'])
def add_criminal():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        dob = request.form['dob']
        gender = request.form['gender']
        record = request.form['record']
        case_id = to_int_or_none(request.form['case_id'])
        age = to_int_or_none(request.form['age'])
        duration = request.form['duration']

        try:
            cursor.execute("""
                INSERT INTO Criminal (Name_, Address, DateofBirth, Gender, CriminalRecord, CaseID, Age, TrialDuration)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, address, dob, gender, record, case_id, age, duration))
            conn.commit()
            flash("✅ Criminal added successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('criminals_page'))

    cursor.execute("SELECT CaseID, CaseType FROM CaseTable;")
    cases = cursor.fetchall()
    conn.close()
    return render_template('add_criminal.html', cases=cases)

@app.route('/edit_criminal/<int:cid>', methods=['GET', 'POST'])
def edit_criminal(cid):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        dob = request.form['dob']
        gender = request.form['gender']
        record = request.form['record']
        case_id = to_int_or_none(request.form['case_id'])
        age = to_int_or_none(request.form['age'])
        duration = request.form['duration']

        try:
            cursor.execute("""
                UPDATE Criminal
                SET Name_=%s, Address=%s, DateofBirth=%s, Gender=%s, CriminalRecord=%s, 
                    CaseID=%s, Age=%s, TrialDuration=%s
                WHERE Criminal_ID=%s
            """, (name, address, dob, gender, record, case_id, age, duration, cid))
            conn.commit()
            flash("✅ Criminal record updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error updating record: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('criminals_page'))

    cursor.execute("SELECT * FROM Criminal WHERE Criminal_ID=%s", (cid,))
    criminal = cursor.fetchone()
    cursor.execute("SELECT CaseID, CaseType FROM CaseTable;")
    cases = cursor.fetchall()
    conn.close()
    return render_template('edit_criminal.html', criminal=criminal, cases=cases)

@app.route('/delete_criminal/<int:cid>', methods=['POST'])
def delete_criminal(cid):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Criminal WHERE Criminal_ID=%s", (cid,))
        conn.commit()
        flash("🗑️ Criminal deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"⛔ Error deleting record: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('criminals_page'))

# ====================== DEPARTMENTS ======================
@app.route('/departments')
def departments_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    head = request.args.get('head', '').strip()

    cursor.execute("""
        CREATE OR REPLACE VIEW DeptSummary AS
        SELECT d.Dept_ID, d.DepartmentType, d.DepartmentHead, d.PhoneNumber, d.Email, d.EstablishedDate,
               COUNT(DISTINCT p.PoliceID) AS OfficerCount,
               COUNT(DISTINCT c.CaseID) AS CaseCount
        FROM Department d
        LEFT JOIN Police p ON d.Dept_ID = p.Dept_ID
        LEFT JOIN CaseTable c ON p.PoliceID = c.AssignedOfficer_ID
        GROUP BY d.Dept_ID;
    """)

    query = "SELECT * FROM DeptSummary"
    params = []
    if head:
        query += " WHERE DepartmentHead LIKE %s"
        params.append(f"%{head}%")
    query += ";"

    cursor.execute(query, params)
    departments = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS dept_count FROM Department;")
    dept_count = cursor.fetchone()['dept_count']
    cursor.execute("SELECT COUNT(*) AS officer_total FROM Police;")
    officer_total = cursor.fetchone()['officer_total']
    cursor.execute("SELECT COUNT(*) AS case_total FROM CaseTable;")
    case_total = cursor.fetchone()['case_total']

    conn.close()
    return render_template('departments.html',
                           departments=departments,
                           dept_count=dept_count,
                           officer_total=officer_total,
                           case_total=case_total)

@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        dept_type = request.form['department_type']
        head = request.form['department_head']
        phone = request.form['phone']
        email = request.form['email']
        est_date = request.form['established_date']

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Department (DepartmentType, DepartmentHead, PhoneNumber, Email, EstablishedDate)
                VALUES (%s, %s, %s, %s, %s)
            """, (dept_type, head, phone, email, est_date))
            conn.commit()
            flash("✅ Department added successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('departments_page'))
    return render_template('add_department.html')

@app.route('/edit_department/<int:dept_id>', methods=['GET', 'POST'])
def edit_department(dept_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        dept_type = request.form['department_type']
        head = request.form['department_head']
        phone = request.form['phone']
        email = request.form['email']
        est_date = request.form['established_date']

        try:
            cursor.execute("""
                UPDATE Department
                SET DepartmentType=%s, DepartmentHead=%s, PhoneNumber=%s, Email=%s, EstablishedDate=%s
                WHERE Dept_ID=%s
            """, (dept_type, head, phone, email, est_date, dept_id))
            conn.commit()
            flash("✅ Department updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Update failed: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('departments_page'))

    cursor.execute("SELECT * FROM Department WHERE Dept_ID=%s", (dept_id,))
    dept = cursor.fetchone()
    conn.close()
    return render_template('edit_department.html', dept=dept)

@app.route('/delete_department/<int:dept_id>', methods=['POST'])
def delete_department(dept_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # if you want to hard-delete a department, you must first detach dependents
        # Option A (restrict): block deletion if in use
        cursor.execute("SELECT COUNT(*) FROM Police WHERE Dept_ID=%s", (dept_id,))
        if cursor.fetchone()[0] > 0:
            flash("⛔ Can't delete: Officers still assigned to this department.", "error")
            conn.close()
            return redirect(url_for('departments_page'))

        cursor.execute("SELECT COUNT(*) FROM Station WHERE Dept_ID=%s", (dept_id,))
        if cursor.fetchone()[0] > 0:
            flash("⛔ Can't delete: Stations still linked to this department.", "error")
            conn.close()
            return redirect(url_for('departments_page'))

        # safe to delete
        cursor.execute("DELETE FROM Department WHERE Dept_ID=%s", (dept_id,))
        conn.commit()
        flash("🗑️ Department deleted!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"⛔ Delete failed: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('departments_page'))

# ====================== STATIONS ======================
@app.route('/stations')
def stations_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    name = request.args.get('name', '').strip()
    officer = request.args.get('officer', '').strip()

    query = """
        SELECT 
            s.Station_ID,
            s.StationName,
            s.Location,
            s.ContactNumber,
            d.DepartmentType AS Department,
            p.PoliceName AS InChargeOfficer
        FROM Station s
        LEFT JOIN Department d ON s.Dept_ID = d.Dept_ID
        LEFT JOIN Police p ON s.InChargeOfficer_ID = p.PoliceID
        WHERE 1=1
    """
    params = []
    if name:
        query += " AND s.StationName LIKE %s"; params.append(f"%{name}%")
    if officer:
        query += " AND p.PoliceName LIKE %s"; params.append(f"%{officer}%")
    query += ";"
    cursor.execute(query, params)
    stations = cursor.fetchall()
    conn.close()
    return render_template('stations.html', stations=stations)

@app.route('/add_station', methods=['GET', 'POST'])
def add_station():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        contact = request.form['contact']
        dept_id = to_int_or_none(request.form['dept'])
        incharge = to_int_or_none(request.form.get('incharge'))

        try:
            cursor.execute("""
                INSERT INTO Station (StationName, Location, ContactNumber, Dept_ID, InChargeOfficer_ID)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, location, contact, dept_id, incharge))
            conn.commit()
            flash("✅ Station added successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error adding station: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('stations_page'))

    cursor.execute("SELECT Dept_ID, DepartmentType FROM Department")
    departments = cursor.fetchall()
    cursor.execute("SELECT PoliceID, PoliceName FROM Police")
    officers = cursor.fetchall()
    conn.close()
    return render_template('add_station.html', departments=departments, officers=officers)

@app.route('/delete_station/<int:station_id>', methods=['POST'])
def delete_station(station_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Station WHERE Station_ID = %s", (station_id,))
        conn.commit()
        flash("🗑️ Station deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"⛔ Error deleting station: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('stations_page'))

# ====================== COURT ======================
@app.route('/court')
def court_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    proceeding_id = request.args.get('proceeding', '').strip()
    case_id = request.args.get('case', '').strip()
    court = request.args.get('court', '').strip()
    judge = request.args.get('judge', '').strip()
    police_id = request.args.get('police', '').strip()

    query = """
        SELECT 
            cp.ProceedingID,
            cp.CaseID,
            c.CaseType,
            c.DateReported,
            cp.ProceedingDate,
            cp.CourtName,
            cp.JudgeName,
            cp.ProceedingType,
            p.PoliceName AS OfficerName,
            d.DepartmentType AS OfficerDepartment,
            cp.Remarks,
            DATEDIFF(cp.ProceedingDate, c.DateReported) AS DaysSinceReport
        FROM CourtProceedings cp
        LEFT JOIN CaseTable c ON cp.CaseID = c.CaseID
        LEFT JOIN Police p ON cp.PoliceID = p.PoliceID
        LEFT JOIN Department d ON p.Dept_ID = d.Dept_ID
        WHERE 1=1
    """
    params = []
    if proceeding_id:
        query += " AND cp.ProceedingID = %s"; params.append(proceeding_id)
    if case_id:
        query += " AND cp.CaseID = %s"; params.append(case_id)
    if court:
        query += " AND cp.CourtName LIKE %s"; params.append(f"%{court}%")
    if judge:
        query += " AND cp.JudgeName LIKE %s"; params.append(f"%{judge}%")
    if police_id:
        query += " AND cp.PoliceID = %s"; params.append(police_id)
    query += " ORDER BY cp.ProceedingDate DESC;"

    cursor.execute(query, params)
    proceedings = cursor.fetchall()

    cursor.execute("""
        SELECT 
            COUNT(cp.ProceedingID) AS total_proceedings,
            COUNT(DISTINCT cp.CaseID) AS distinct_cases,
            COUNT(DISTINCT cp.PoliceID) AS officers_involved,
            AVG(DATEDIFF(cp.ProceedingDate, c.DateReported)) AS avg_days_delay
        FROM CourtProceedings cp
        LEFT JOIN CaseTable c ON cp.CaseID = c.CaseID;
    """)
    stats = cursor.fetchone()
    conn.close()
    return render_template('court.html', proceedings=proceedings, stats=stats)

@app.route('/add_court', methods=['GET', 'POST'])
def add_court():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        case_id = to_int_or_none(request.form.get('CaseID'))
        proc_date = request.form['ProceedingDate']
        court_name = request.form['CourtName']
        judge_name = request.form['JudgeName']
        proc_type = request.form['ProceedingType']
        police_id = to_int_or_none(request.form.get('PoliceID'))
        remarks = to_none_if_empty(request.form.get('Remarks'))

        try:
            cursor.execute("""
                INSERT INTO CourtProceedings 
                (CaseID, ProceedingDate, CourtName, JudgeName, ProceedingType, PoliceID, Remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (case_id, proc_date, court_name, judge_name, proc_type, police_id, remarks))
            conn.commit()
            flash("✅ Court proceeding added successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('court_page'))

    cursor.execute("SELECT CaseID, CaseType FROM CaseTable;")
    cases = cursor.fetchall()
    cursor.execute("SELECT PoliceID, PoliceName FROM Police;")
    officers = cursor.fetchall()
    conn.close()
    return render_template('add_court.html', cases=cases, officers=officers)

@app.route('/edit_court/<int:proc_id>', methods=['GET', 'POST'])
def edit_court(proc_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        case_id = to_int_or_none(request.form.get('CaseID'))
        proc_date = request.form['ProceedingDate']
        court_name = request.form['CourtName']
        judge_name = request.form['JudgeName']
        proc_type = request.form['ProceedingType']
        police_id = to_int_or_none(request.form.get('PoliceID'))
        remarks = to_none_if_empty(request.form.get('Remarks'))

        try:
            cursor.execute("""
                UPDATE CourtProceedings
                SET CaseID=%s, ProceedingDate=%s, CourtName=%s, JudgeName=%s, 
                    ProceedingType=%s, PoliceID=%s, Remarks=%s
                WHERE ProceedingID=%s
            """, (case_id, proc_date, court_name, judge_name, proc_type, police_id, remarks, proc_id))
            conn.commit()
            flash("✅ Court proceeding updated!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"⛔ Error: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('court_page'))

    cursor.execute("SELECT * FROM CourtProceedings WHERE ProceedingID=%s", (proc_id,))
    proc = cursor.fetchone()
    cursor.execute("SELECT CaseID, CaseType FROM CaseTable;")
    cases = cursor.fetchall()
    cursor.execute("SELECT PoliceID, PoliceName FROM Police;")
    officers = cursor.fetchall()
    conn.close()
    return render_template('edit_court.html', proc=proc, cases=cases, officers=officers)

@app.route('/delete_court/<int:proc_id>', methods=['POST'])
def delete_court(proc_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM CourtProceedings WHERE ProceedingID=%s", (proc_id,))
        conn.commit()
        flash("🗑️ Court proceeding deleted!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"⛔ Error: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('court_page'))

# ====================== EVIDENCE ======================
@app.route('/evidence')
def evidence_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    evi_type = request.args.get('type', '').strip()
    collected_by = request.args.get('officer', '').strip()
    case_id = request.args.get('case', '').strip()

    query = """
        SELECT 
            e.EvidenceID,
            e.EvidenceType,
            e.Description,
            e.DateCollected,
            e.StorageLocation,
            c.CaseType,
            p.PoliceName AS CollectedBy,
            DATEDIFF(CURDATE(), e.DateCollected) AS DaysOld
        FROM Evidence e
        JOIN CaseTable c ON e.CaseID = c.CaseID
        LEFT JOIN Police p ON e.CollectedBy = p.PoliceID
        WHERE 1=1
    """
    params = []
    if evi_type:
        query += " AND e.EvidenceType LIKE %s"; params.append(f"%{evi_type}%")
    if collected_by:
        query += " AND p.PoliceName LIKE %s"; params.append(f"%{collected_by}%")
    if case_id:
        query += " AND e.CaseID = %s"; params.append(case_id)
    query += " ORDER BY e.DateCollected DESC;"

    cursor.execute(query, params)
    evidences = cursor.fetchall()

    cursor.execute("""
        SELECT c.CaseType, COUNT(e.EvidenceID) AS TotalEvidence
        FROM CaseTable c
        LEFT JOIN Evidence e ON c.CaseID = e.CaseID
        GROUP BY c.CaseType
        HAVING TotalEvidence > 0;
    """)
    evidence_summary = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total, AVG(DATEDIFF(CURDATE(), DateCollected)) AS avg_age FROM Evidence;")
    stats = cursor.fetchone()

    conn.close()
    return render_template('evidence.html',
                           evidences=evidences,
                           evidence_summary=evidence_summary,
                           stats=stats)

@app.route('/view_evidence/<int:case_id>')
def view_evidence(case_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            e.EvidenceID,
            e.EvidenceType,
            e.Description,
            e.DateCollected,
            e.StorageLocation,
            p.PoliceName AS CollectedBy
        FROM Evidence e
        LEFT JOIN Police p ON e.CollectedBy = p.PoliceID
        WHERE e.CaseID = %s
        ORDER BY e.DateCollected DESC;
    """, (case_id,))
    evidence = cursor.fetchall()

    cursor.execute("SELECT CaseID, CaseType, Description_Of_Case FROM CaseTable WHERE CaseID = %s", (case_id,))
    case = cursor.fetchone()

    conn.close()
    return render_template('case_evidence.html', evidence=evidence, case=case)

# ====================== DASHBOARD ======================
@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CriminalCaseSummaryView;")
    summary = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total_cases FROM CriminalCaseSummaryView;")
    total_cases = cursor.fetchone()['total_cases']
    cursor.execute("SELECT COUNT(DISTINCT CriminalName) AS total_criminals FROM CriminalCaseSummaryView;")
    total_criminals = cursor.fetchone()['total_criminals']
    cursor.execute("SELECT COUNT(DISTINCT AssignedOfficer) AS total_officers FROM CriminalCaseSummaryView;")
    total_officers = cursor.fetchone()['total_officers']
    cursor.execute("SELECT ROUND(AVG(ProgressPercentage), 2) AS avg_progress FROM CriminalCaseSummaryView;")
    avg_progress = cursor.fetchone()['avg_progress']

    conn.close()
    return render_template('dashboard.html',
                           summary=summary,
                           total_cases=total_cases,
                           total_criminals=total_criminals,
                           total_officers=total_officers,
                           avg_progress=avg_progress)

if __name__ == '__main__':
    # debug=True is fine for dev; turn off in prod
    app.run(debug=True)
