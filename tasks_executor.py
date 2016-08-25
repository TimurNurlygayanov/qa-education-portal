import os
import time
import uuid
import subprocess
from multiprocessing import Process, Queue
from pymongo import MongoClient


UPLOAD_FOLDER = '/tmp/tasks/'
ALLOWED_EXTENSIONS = set(['py', 'sh'])

queue = Queue()
threads_count = 1
db_client = MongoClient()
db = db_client.tasks_database
tasks = db.tasks
tasks.remove({})

def execute_task(queue):
    if not queue.empty():
        task = queue.get(timeout=1)

        filename = task['task_file']
        task_id = task['uid']
        tasks.update({'uid': task_id}, {'$set': {'status': 'in_progress'} })

        cmd = "cp {0}{1} {2} ; python {2}{1}".format(UPLOAD_FOLDER,
                                                     filename,
                                                     "/tmp/")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        output = process.communicate()[0]
        returncode = process.returncode

	tasks.update({'uid': task_id}, {'$set': {'status': 'done',
                                                 'result': {'output': output, 'returncode': returncode}}})


if __name__ == '__main__':
    while True:

        # read database and put new tasks to queue:
        for new_task in tasks.find({'status': 'in_queue'}):
            queue.put(new_task, timeout=10)
            # woraround for queue.put:
            time.sleep(0.01)

        while not queue.empty():
            workers = [Process(target=execute_task, args=(queue,))
                       for i in xrange(threads_count)]
            for w in workers:
                w.daemon = True
            [w.start() for w in workers]

            for w in workers:
                w.join(timeout=0.1)
