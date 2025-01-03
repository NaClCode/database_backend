from model.ClassScheduleModel import ClassSchedule
from model.SCModel import StudentCourse
from model.ClassModel import Class
from model.EnrollmentHistoryModel import EnrollmentHistory
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.sql import select

class EnrollCrud:
    @staticmethod
    def check_schedule_conflict(db: Session, student_id: int, new_class_id: int):
        """
        检测是否课程冲突
        """

        new_schedules = db.query(ClassSchedule).filter_by(class_id=new_class_id).all()
        enrolled_class_ids_stmt = select(StudentCourse.class_id).filter_by(student_id=student_id)
        schedules = db.query(ClassSchedule).filter(ClassSchedule.class_id.in_(enrolled_class_ids_stmt)).all()

        for ns in new_schedules:
            for es in schedules:
                if ns.start_time < es.end_time and es.start_time < ns.end_time:
                    return True

        return False

    @staticmethod
    def enroll_course(db: Session, student_id: int, class_id: int, time: datetime):
        """
        选课
        """
        course = db.query(Class).filter_by(id=class_id).first()
        if not course:
            raise ValueError("课程不存在")

        class_plan_id = course.class_plan_id
        existing_class = (
            db.query(StudentCourse)
            .join(Class, StudentCourse.class_id == Class.id)
            .filter(StudentCourse.student_id == student_id, Class.class_plan_id == class_plan_id)
            .first()
        )

        if existing_class:
            raise ValueError("已经选了该课程计划中的课")

        course = db.query(Class).with_for_update().filter_by(id=class_id).first()
        if course.num >= course.max_num:
            raise ValueError("课程人数满了")

        conflict_state = EnrollCrud.check_schedule_conflict(db, student_id, class_id)
        if conflict_state:
            raise ValueError("课程冲突")

        enrollment = StudentCourse(student_id=student_id, class_id=class_id, enrolled_date=time)
        db.add(enrollment)

        history = EnrollmentHistory(student_id=student_id, class_id=class_id, action_type='Enroll', action_date=time)
        db.add(history)

        course.num += 1
        db.commit()
        return True

    @staticmethod
    def drop_course(db:Session, student_id:int, class_id:int, time:datetime):
        """
        退课
        """
        enrollment = db.query(StudentCourse).filter_by(student_id=student_id, class_id=class_id).first()
        if not enrollment:
            raise ValueError("没有选该课")

        db.delete(enrollment)

        history = EnrollmentHistory(student_id=student_id, class_id=class_id, action_type='Drop', action_date=time)
        db.add(history)

        course = db.query(Class).with_for_update().filter_by(id=class_id).first()
        course.num -= 1
        db.commit()
        return True