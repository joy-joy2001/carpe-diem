import datetime as dt
from flask import request
from uuid import uuid4
from BoardHandler import db
from UsersHandler import get_user_board

date = dt.date

priorityLvls = {
    'high': "red",
    'medium': 'orange',
    'low': 'green',
}


def kanban_stats():
    all_lists = create_board()
    today = date.today()
    month = today.strftime("%B")[slice(3)].upper()
    year = today.strftime("%Y")
    stats = {
        'todo_no': len(all_lists['todo_list']),
        'inprogress_no': len(all_lists['progress_list']),
        'completed_no': len(all_lists['completed_list']),
        'total': (len(all_lists['todo_list']) + len(all_lists['progress_list']) + len(all_lists['completed_list'])),
        'date': f'{month} {year}'
    }
    return stats


def current_date():
    today = date.today()
    current_month = today.strftime("%m")
    current_day = today.strftime("%d")
    return f"{current_day}/{current_month}"


def create_board():
    user_board = get_user_board()
    todo_list = db.session.query(user_board).filter_by(type='todo').all()
    inprogress_list = db.session.query(user_board).filter_by(type='in_progress').all()
    completed_list = db.session.query(user_board).filter_by(type='completed').all()
    all_lists = {
        'todo_list': todo_list,
        'progress_list': inprogress_list,
        'completed_list': completed_list,
    }
    return all_lists


def create_task():
    table = get_user_board()
    new_task = table.insert().values(
        id=str(uuid4()),
        type='todo',
        desc=request.form.get('task-details'),
        priority=priorityLvls[request.form.get('task-priority')],
        due_date=f"{request.form.get('task-duedate').split('-')[2]}/{request.form.get('task-duedate').split('-')[1]}",
        created_date=current_date(),
    )

    db_connection = db.engine.connect()
    db_connection.execute(new_task)


def delete_task():
    user_board = get_user_board()
    print(user_board)
    print(type(user_board))
    task_id = request.args.get('task_id')
    db.session.query(user_board).filter_by(id=task_id).delete()
    db.session.commit()


def promote_task():
    user_board = get_user_board()
    current_task_id = request.args.get('task_id')
    current_task = db.session.query(user_board).filter_by(id=current_task_id).first()
    if current_task['type'] == 'todo':
        # print("yes its a todo task!")
        db.session.query(user_board).filter_by(id=current_task_id).update(dict(type='in_progress'))
        db.session.commit()
    elif current_task['type'] == 'in_progress':
        # print('yes its a inprogress task')
        db.session.query(user_board).filter_by(id=current_task_id).update(dict(type='completed'))
        db.session.commit()


def demote_task():
    user_board = get_user_board()
    current_task_id = request.args.get('task_id')
    current_task = db.session.query(user_board).filter_by(id=current_task_id).first()
    if current_task['type'] == 'completed':
        db.session.query(user_board).filter_by(id=current_task_id).update(dict(type='in_progress'))
        db.session.commit()
    elif current_task['type'] == 'in_progress':
        db.session.query(user_board).filter_by(id=current_task_id).update(dict(type='todo'))
        db.session.commit()

