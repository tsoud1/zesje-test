""" Models used in the db """

from datetime import datetime
import random
import string
import hashlib

from pony.orm import db_session, Database, Required, Optional, PrimaryKey, Set

# from https://editor.ponyorm.com/user/zesje/zesje/python

db = Database()


# Helper functions #
# Have to appear at the top of the file, because otherwise they won't be defined when the models are defined


def _generate_exam_token():
    hasher = hashlib.sha1() 
    N = 12 #length of hash
    while True:
        hash_input = Exam.name + Exam.id
        hasher.update(hash_input.encode('utf-8'))
        token_string = hasher.hexdigest()[0:N]# cap the hash at N 
        
        with db_session:
            if not Exam.select(lambda e: e.token == token_string).exists():
                return token_string


# Models #

class Student(db.Entity):
    """New students may be added throughout the course."""
    id = PrimaryKey(int)
    first_name = Required(str)
    last_name = Required(str)
    email = Optional(str, unique=True)
    submissions = Set('Submission')


class Grader(db.Entity):
    """Graders can be created by any user at any time, but are immutable once they are created"""
    name = Required(str)
    graded_solutions = Set('Solution')


class Exam(db.Entity):
    """ New instances are created when providing a new exam. """
    name = Required(str)
    token = Required(str, unique=True, default=_generate_exam_token)
    submissions = Set('Submission')
    problems = Set('Problem')
    scans = Set('Scan')
    widgets = Set('ExamWidget')
    finalized = Required(bool, default=False)


class Submission(db.Entity):
    """Typically created when adding a new exam."""
    copy_number = Required(int)
    exam = Required(Exam)
    solutions = Set('Solution')
    pages = Set('Page')
    student = Optional(Student)
    signature_validated = Required(bool, default=False)


class Page(db.Entity):
    """Page of an exam"""
    path = Required(str)
    submission = Required(Submission)
    number = Required(int)


class Problem(db.Entity):
    """this will be initialized @ app initialization and immutable from then on."""
    name = Required(str)
    exam = Required(Exam)
    feedback_options = Set('FeedbackOption')
    solutions = Set('Solution')
    widget = Required('ProblemWidget')


class FeedbackOption(db.Entity):
    """feedback option -- can be shared by multiple problems.
    this means non-duplicate rows for things like 'all correct',
    but means that care must be taken when "updating" and "deleting"
    options from the UI (not yet supported)"""
    problem = Required(Problem)
    text = Required(str)
    description = Optional(str)
    score = Optional(int)
    solutions = Set('Solution')


class Solution(db.Entity):
    """solution to a single problem"""
    submission = Required(Submission)
    problem = Required(Problem)
    graded_by = Optional(Grader)  # if null, this has not yet been graded
    graded_at = Optional(datetime)
    feedback = Set(FeedbackOption)
    remarks = Optional(str)
    PrimaryKey(submission, problem)


class Scan(db.Entity):
    """Metadata on uploaded PDFs"""
    exam = Required(Exam)
    name = Required(str)
    status = Required(str)
    message = Optional(str)


class Widget(db.Entity):
    id = PrimaryKey(int, auto=True)
    # Can be used to distinguish widgets for barcodes, student_id and problems
    name = Optional(str)
    x = Required(int)
    y = Required(int)


class ExamWidget(Widget):
    exam = Required(Exam)


class ProblemWidget(Widget):
    problem = Optional(Problem)
    page = Required(int)
    width = Required(int)
    height = Required(int)
