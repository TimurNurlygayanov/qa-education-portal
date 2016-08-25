from flask import Flask
from flask import request
from flask import jsonify
import os
import time
import uuid
from werkzeug.utils import secure_filename
import subprocess
from multiprocessing import Process, Queue
from pymongo import MongoClient


UPLOAD_FOLDER = '/tmp/tasks/'
ALLOWED_EXTENSIONS = set(['py', 'sh'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 + 1  # 1 Mb

db_client = MongoClient()
db = db_client.tasks_database


def check_file(f):
    file_format = f.split('.')[-1]
    return file_format in ALLOWED_EXTENSIONS



@ app.errorhandler(413)
def err_413(error):
    return "The size of file is too large, sorry.", 413


@app.route('/tasks', methods=['GET'])
def list_tasks():
    response = {}
    tasks = db.tasks
    for task in tasks.find():
        print task
        response[task['uid']] = {'uid': task['uid'],
                                'status': task['status'],
                                'result': task['result']}
    return jsonify(response)


@app.route('/run_task', methods=['POST'])
def run_task():
    if request.method == 'POST':
        print request.data
        user = '' #str(request.data.get('user', ''))
        task_id = uuid.uuid4().hex

        task_file = request.files.get('file', None)

        if task_file is not None:
            check_file(task_file.filename)
            filename = secure_filename(task_file.filename)
            task_file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                        filename))

            task = {'uid': task_id, 'user': user,
                    'status': 'in_queue', 'type': 'pytest',
                    'task_file': task_file.filename,
                    'result': {'output': '', 'returncode': 0}}

            tasks = db.tasks
            tasks.insert_one(task)

            response = {'uid': task_id}
            return app.make_response(jsonify(response))
        else:
            response = {'error': 'incorrect data!'}
            return app.make_response(jsonify(response)), 400


if __name__ == '__main__':
    app.run(debug=True)
