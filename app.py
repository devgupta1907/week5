from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


fapp = Flask(__name__)
fapp.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"

db = SQLAlchemy()
db.init_app(fapp)
fapp.app_context().push()


class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)
    
class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable=False)


@fapp.route("/", methods=["GET", "POST"])
def students():
    students = Student.query.all()
    return render_template("index.html", students=students)

@fapp.route("/student/create", methods=["GET", "POST"])
def add_student():
    if request.method == "GET":
        return render_template("add_student.html")
    roll_number = request.form.get("roll")
    first_name = request.form.get("f_name")
    last_name = request.form.get("l_name")
    courses = request.form.getlist("courses")
    
    is_apna_baccha = Student.query.filter_by(roll_number=roll_number).first()
    if is_apna_baccha:
        message = "Student already exists. Please use different Roll Number!"
        return render_template("add_student.html", message=message)
    
    naya_bachha = Student(roll_number=roll_number, first_name=first_name, last_name=last_name)
    
    db.session.add(naya_bachha)
    db.session.commit()
    
    for course in courses:
        course_detail = Course.query.filter_by(course_name=course).first()
        if course_detail:
            enrol = Enrollments(estudent_id=naya_bachha.student_id, ecourse_id=course_detail.course_id)
            db.session.add(enrol)
    db.session.commit()
        
    return redirect(url_for("students"))



@fapp.route("/student/<int:student_id>", methods=["GET", "POST"])
def student_details(student_id):
    if request.method=="GET":
        apna_baccha = Student.query.filter_by(student_id=student_id).first()
        apna_baccha_enrolments = Enrollments.query.filter_by(estudent_id=student_id)
        apna_baccha_courses = []
        for e in apna_baccha_enrolments:
            course = Course.query.filter_by(course_id=e.ecourse_id).first()
            apna_baccha_courses.append(course)
        return render_template("student_details.html", student=apna_baccha, courses=apna_baccha_courses)


        
@fapp.route("/student/<int:student_id>/update", methods=["GET", "POST"])
def update_student(student_id):
    if request.method == "GET":
        apna_baccha = Student.query.filter_by(student_id=student_id).first()
        if apna_baccha:
            current_roll = apna_baccha.roll_number
            current_f_name = apna_baccha.first_name
            current_l_name = apna_baccha.last_name
            return render_template("update_student.html", student_id=student_id, current_roll=current_roll, current_f_name=current_f_name, current_l_name=current_l_name)
    
    new_first_name = request.form.get("f_name")
    new_last_name = request.form.get("l_name")
    new_courses = request.form.getlist("courses")
    
    apna_baccha = Student.query.filter_by(student_id=student_id).first()
    apna_baccha.first_name = new_first_name
    apna_baccha.last_name = new_last_name
    
    db.session.add(apna_baccha)
    db.session.commit()
    
    Enrollments.query.filter_by(estudent_id=apna_baccha.student_id).delete()
    for course in new_courses:
        course_detail = Course.query.filter_by(course_name=course).first()
        if course_detail:
            enrol = Enrollments(estudent_id=apna_baccha.student_id, ecourse_id=course_detail.course_id)
            db.session.add(enrol)
    db.session.commit()
    
    return redirect(url_for("students"))



@fapp.route("/student/<int:student_id>/delete", methods=["GET", "POST"])
def delete_student(student_id):
    if request.method == "GET":
        Student.query.filter_by(student_id=student_id).delete()
        Enrollments.query.filter_by(estudent_id=student_id).delete()
        db.session.commit()
        
        return redirect(url_for("students"))
    



if __name__ == "__main__":
    fapp.run(debug=True)