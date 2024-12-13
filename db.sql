use database_exp;

CREATE TABLE student (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    idcard CHAR(18),
    sex ENUM('M', 'F', 'U') NOT NULL,
    password VARCHAR(255) NOT NULL,
    age INTEGER,
    classer VARCHAR(50),
    profession VARCHAR(100),
    college VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    verify BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE teacher (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    idcard CHAR(18),
    password VARCHAR(255) NOT NULL,
    sex ENUM('M', 'F', 'U') NOT NULL,
    introduction VARCHAR(255),
    profession VARCHAR(100),
    college VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    verify BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE class (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    num INTEGER NOT NULL DEFAULT 0,
    max_num INTEGER NOT NULL,
    class_plan_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY(class_plan_id) REFERENCES class_plan(id),
    FOREIGN KEY(teacher_id) REFERENCES teacher(id)
);
CREATE TABLE class_plan (
    id INTEGER NOT NULL AUTO_INCREMENT, -- Class plan ID, primary key, auto-increment
    name VARCHAR(100) NOT NULL,         -- Class name, max length 100 characters, not null
    introduction VARCHAR(255),          -- Introduction, max length 255 characters, nullable
    profession VARCHAR(100),            -- Profession, max length 100 characters, nullable
    college VARCHAR(100),               -- College, max length 100 characters, nullable
    credit INTEGER NOT NULL,            -- Credits, not null
    type ENUM('B', 'X', 'G', 'S') NOT NULL, -- Class type: B-Mandatory, X-Elective, G-Public, S-Practice, not null
    PRIMARY KEY (id)                    -- Primary key on 'id'
);
CREATE TABLE class_schedule (
    id INTEGER NOT NULL AUTO_INCREMENT, -- Course schedule ID, primary key, auto-increment
    start_time DATETIME NOT NULL,       -- Start time, not null
    end_time DATETIME NOT NULL,         -- End time, not null
    classtype ENUM('C', 'S') NOT NULL,  -- Class type: C-Classroom, S-Lab, not null
    classroom VARCHAR(100),             -- Classroom, nullable, max length 100 characters
    class_id INTEGER NOT NULL,          -- Class ID, foreign key, not null
    PRIMARY KEY (id),                   -- Primary key on 'id'
    FOREIGN KEY (class_id) REFERENCES class(id) -- Foreign key reference to 'class' table
);
CREATE TABLE enrollment_history (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    action_type ENUM ('Enroll', 'Drop') NOT NULL,
    action_date DATETIME NOT NULL,
    FOREIGN KEY(student_id) REFERENCES student(id),
    FOREIGN KEY(class_id) REFERENCES class(id)
);
CREATE TABLE feedback (
    feedback_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    content TEXT,
    created INTEGER NOT NULL,
    is_read INTEGER NOT NULL
);
CREATE TABLE student_course (
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    grade FLOAT,
    enrolled_date DATETIME NOT NULL,
    PRIMARY KEY(student_id, class_id),
    FOREIGN KEY(student_id) REFERENCES student(id),
    FOREIGN KEY(class_id) REFERENCES class(id)
);