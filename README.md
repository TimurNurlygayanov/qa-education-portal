# Start Application
python api_server.py

python tasks_executor.py

# Add new task to the queue
curl -i -X POST -H "Content-Type: multipart/form-data" -F "file=@w2.py" http://127.0.0.1:5000/run_task

# Get list of tasks
curl -X GET http://127.0.0.1:5000/tasks
