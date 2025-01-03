from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from typing import List, Union
from model.SCModel import StudentCourse
from model.ClassModel import Class
from model.ClassScheduleModel import ClassSchedule
from model.ClassPlanModel import ClassPlan
from model.StudentModel import Student

class StudentCourseCrud:
    @staticmethod
    def create(db: Session, student_id: int, class_id: int, enrolled_date, grade: float = None) -> StudentCourse:
        """
        创建学生选课记录
        """
        new_record = StudentCourse(
            student_id=student_id,
            class_id=class_id,
            enrolled_date=enrolled_date,
            grade=-1
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record

    @staticmethod
    def get_by_student_and_class(db: Session, student_id: int, class_id: int) -> Union[StudentCourse, None]:
        """
        根据学生ID和课程班级ID获取选课记录
        """
        return db.query(StudentCourse).filter(
            StudentCourse.student_id == student_id,
            StudentCourse.class_id == class_id
        ).first()

    @staticmethod
    def get_by_student_id(db: Session, student_id: int) -> List[StudentCourse]:
        """
        根据学生ID获取该学生的所有选课记录
        """
        return db.query(StudentCourse).filter(StudentCourse.student_id == student_id).all()

    @staticmethod
    def get_by_class_id(db: Session, class_id: int) -> List[StudentCourse]:
        """
        根据课程班级ID获取所有学生选课记录
        """
        return db.query(StudentCourse).filter(StudentCourse.class_id == class_id).all()

    @staticmethod
    def get_all(db: Session) -> List[StudentCourse]:
        """
        获取所有选课记录
        """
        return db.query(StudentCourse).all()

    @staticmethod
    def update(db: Session, record: StudentCourse, **kwargs) -> StudentCourse:
        """
        更新选课记录，kwargs为需要更新的字段和值
        """
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def delete(db: Session, record: StudentCourse) -> StudentCourse:
        """
        删除选课
        """
        db.delete(record)
        db.commit()
        return record

    @staticmethod
    def delete_by_student_and_class(db: Session, student_id: int, class_id: int) -> Union[StudentCourse, None]:
        """
        根据学生ID和课程班级ID删除选课
        """
        record = StudentCourseCrud.get_by_student_and_class(db, student_id, class_id)
        if record:
            db.delete(record)
            db.commit()
        return record
    
    @staticmethod
    def get_courses_by_month(db: Session, student_id: int, month: int, year: int) -> List[dict]:
        """
        获取学生在某个月份的所有选课记录，通过class_schedule中的start_time筛选，
        并从class_plan中获取课程名称以及该课程这个月的所有安排。
        """
        records = db.query(ClassPlan.name, ClassSchedule.start_time).join(
            Class, ClassPlan.id == Class.class_plan_id
        ).join(
            ClassSchedule, Class.id == ClassSchedule.class_id
        ).join(
            StudentCourse, StudentCourse.class_id == Class.id
        ).filter(
            StudentCourse.student_id == student_id,
            extract('month', ClassSchedule.start_time) == month,
            extract('year', ClassSchedule.start_time) == year
        ).all()

        course_details = [
            {"name": name, "date": start_time}
            for name, start_time in records
        ]

        return course_details
    
    @staticmethod
    def get_courses_by_day(db: Session, student_id: int, specific_date: datetime) -> List[dict]:
     """
     获取学生在某一天的课程信息，包括课程名称、时间和上课地点
     """
     from sqlalchemy.sql import func

     course_details = db.query(
        ClassPlan.name.label('course_name'),
        ClassSchedule
     ).select_from(StudentCourse).join(
        Class, StudentCourse.class_id == Class.id
     ).join(
        ClassPlan, ClassPlan.id == Class.class_plan_id
     ).join(
        ClassSchedule, ClassSchedule.class_id == Class.id
     ).filter(
        StudentCourse.student_id == student_id,
        func.date(ClassSchedule.start_time) == specific_date.date()
     ).all()

     return [{
          'name': name,
          'start_time': course.start_time,
          'end_time': course.end_time,
          'classroom': course.classroom
        }
        for name, course in course_details
    ]

    @staticmethod
    def get_student_grade_page(
        db: Session, student_id: int, page: int = 1, page_size: int = 10
    ) -> dict:
        """
        获取学生所有课程的详细信息，包括课程号、课程名称、专业、学院、类型、学分、教师、分数
        支持分页
        """
        offset = (page - 1) * page_size
        query = db.query(
            Class,
            ClassPlan,
            StudentCourse.grade
        ).join(
            StudentCourse, StudentCourse.class_id == Class.id
        ).join(
            ClassPlan, ClassPlan.id == Class.class_plan_id
        ).filter(
            StudentCourse.student_id == student_id
        ).offset(offset).limit(page_size)
        
        records = query.all()
        
        total_records = db.query(StudentCourse).filter(StudentCourse.student_id == student_id).count()
        total_pages = (total_records + page_size - 1) // page_size
        
        course_details = [{
            'course_id': classer.id,
            'course_name': class_plan.name,
            'profession': class_plan.profession,
            'college': class_plan.college,
            'type': class_plan.type,
            'credits': class_plan.credit,
            'teacher': classer.teacher.name,
            'grade': grade
        } for classer, class_plan, grade in records]
        
        return {
            "data": course_details,
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages
        }
    
    @staticmethod
    def get_students_and_grades(db:Session, class_id: int):
        results = (
            db.query(Student.id, Student.name, StudentCourse.grade)
            .join(StudentCourse, Student.id == StudentCourse.student_id)
            .filter(StudentCourse.class_id == class_id)
            .all()
        )
        return results
    
    @staticmethod
    def upload_student_grades(db: Session, class_id: int, student_ids: list, grades: list):
        if len(student_ids) != len(grades):
            raise ValueError("student len != grade len")
        
        for student_id, grade in zip(student_ids, grades):
            record = (
                db.query(StudentCourse)
                .filter(StudentCourse.student_id == student_id, StudentCourse.class_id == class_id)
                .first()
            )
            
            if record:
                record.grade = grade
            else:
                new_record = StudentCourse(
                    student_id=student_id,
                    class_id=class_id,
                    grade=grade,
                    enrolled_date=datetime.now() 
                )
                db.refresh(new_record)
        
        db.commit()
