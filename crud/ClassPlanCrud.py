from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import case
from model.ClassPlanModel import ClassPlan
from model.SCModel import StudentCourse
from model.ClassModel import Class
from .Crud import AbstractCrud

class ClassPlanCrud(AbstractCrud[ClassPlan]):
    @staticmethod
    def create(db: Session, name: str, credit: int, introduction: str = None, 
               profession: str = None, college: str = None) -> ClassPlan:
        """
        创建一个新的课程计划记录
        """
        new_plan = ClassPlan(
            name=name, 
            credit=credit, 
            introduction=introduction, 
            profession=profession, 
            college=college
        )
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return new_plan
    
    @staticmethod
    def get_by_id_paginated(
        db: Session, 
        student_id: int, 
        page: int = 1, 
        page_size: int = 10
    ):
        """
        分页查询 class_plan，并判断指定学生是否选择了该课程。
        """
        offset = (page - 1) * page_size
        
        total_records = db.query(ClassPlan).count()
        total_pages = (total_records + page_size - 1) // page_size

        if page > total_pages:
            return {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "data": []
            }
        
        subquery = (
            db.query(StudentCourse.class_id)
            .join(Class, StudentCourse.class_id == Class.id)
            .filter(
                Class.class_plan_id == ClassPlan.id,
                StudentCourse.student_id == student_id
            )
            .exists()
        )

        data = (
            db.query(
                ClassPlan.id,
                ClassPlan.name,
                ClassPlan.introduction,
                ClassPlan.profession,
                ClassPlan.college,
                ClassPlan.credit,
                ClassPlan.type,
                case((subquery, 1), else_=0).label('is_selected')
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
            "data": [{
                "id": i.id,
                "name": i.name,
                "introduction": i.introduction,
                "profession": i.profession, 
                "college": i.college,
                "credit": i.credit,
                "type": i.type,
                "is_selected": i.is_selected
            } for i in data]
        }

    @staticmethod
    def get_by_filters(
        db: Session, 
        student_id: int, 
        page: int = 1, 
        page_size: int = 10, 
        name: str = None,
        credit: int = None, 
        profession: str = None, 
        type: str = None,
        college: str = None,
        is_selected: bool = None
    ):
        """
        根据 credit, profession, college 等筛选条件查询记录，先过滤再分页查询。
        同时判断指定学生是否选择了该课程计划。
        """

        selected_subquery = (
            db.query(ClassPlan.id)
            .join(Class, ClassPlan.id == Class.class_plan_id)
            .join(StudentCourse, 
                (StudentCourse.class_id == Class.id) & (StudentCourse.student_id == student_id))
            .distinct()
        ).subquery()

        query = db.query(ClassPlan.id,
                        ClassPlan.name,
                        ClassPlan.introduction,
                        ClassPlan.profession,
                        ClassPlan.college,
                        ClassPlan.credit,
                        ClassPlan.type,
                        case(
                            (ClassPlan.id.in_(selected_subquery), 1), else_=0
                        ).label("is_selected"))

        filters = []

        if name != "":
            filters.append(ClassPlan.name == name)
        if credit and credit != -1:
            filters.append(ClassPlan.credit == credit)
        if profession != "":
            filters.append(ClassPlan.profession == profession)
        if college != "":
            filters.append(ClassPlan.college == college)
        if type != "":
            filters.append(ClassPlan.type == type)
        if is_selected != -1:
            if is_selected:
                filters.append(ClassPlan.id.in_(selected_subquery))  # 筛选选中的课程
            else:
                filters.append(~ClassPlan.id.in_(selected_subquery))  # 筛选未选中的课程

        query = query.filter(*filters)

        total_records = query.count()
        total_pages = (total_records + page_size - 1) // page_size

        offset = (page - 1) * page_size
        if page > total_pages:
            return {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "data": []
            }

        data = query.offset(offset).limit(page_size).all()

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
            "data": [
                {
                    "id": i.id,
                    "name": i.name,
                    "introduction": i.introduction,
                    "profession": i.profession, 
                    "college": i.college,
                    "credit": i.credit,
                    "type": i.type,
                    "is_selected": i.is_selected
                }
                for i in data
            ]
        }


   