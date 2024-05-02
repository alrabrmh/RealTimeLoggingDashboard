import requests
import json
from datetime import date
from datetime import datetime
import time
import random
import socket

appId = "BANKHEARTBEAT"

log_queue = []
# function to check if the middleware is alive ?
def isOpen():
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect(('localhost', int(8000)))
      s.shutdown(2)
      return True
   except:
      return False
   
def generate_random_log_message():
   # Generate a random log message type
   log_message_type = random.choice(["error", "info", "create", "delete" , "xyzz"])

   # Generate some random log data based on the message type
   if log_message_type == "error":
       log_data = f"ERROR: Something went wrong!"
   elif log_message_type == "info":
       log_data = f"INFO: Process completed successfully."
   elif log_message_type == "create":
       log_data = f"CREATE: New Order created."
   elif log_message_type == "delete":
       log_data = f"DELETE: order deleted."
   else: 
       log_data = f"XYZ: Test for Phase 2."
    # Define the log message as a dictionary
#    log_msg = {
#         "Id" : appId,
#         "date": date.today().strftime("%d-%m-%Y"),
#         "time": datetime.now().strftime("%H:%M:%S"),
#         "type" : log_message_type,
#         "message" : log_data
#         }
#    return log_msg
   log_msg = '{"Id" : "' + appId + '","date" :"' + date.today().strftime("%d-%m-%Y") + '","time": "' + datetime.now().strftime("%H:%M:%S") + '","type" : "' + log_message_type + '","message" : "' + log_data + '"}'
   return log_msg

def post_logs(logs):
    
    
    if isOpen():
     for log in logs:
       print(f"Posting log: {log}")
       # Make a POST request to the server with the log data
       response = requests.post("http://localhost:8000/log", json=log,headers={
                                                'Content-type':'application/json', 
                                                'Accept':'application/json'
                                            })
       if response.status_code == 200:
           print("Log posted successfully")
    # Clear the queue after attempting to post logs
     log_queue.clear()
    else:
        print("Failed to post log. Adding it to the queue.")
 
while True:
   log_message = generate_random_log_message()
   log_queue.append(log_message)

   # Try to post logs from the queue
   post_logs(log_queue)

   time.sleep(10)  # Wait for 10 seconds