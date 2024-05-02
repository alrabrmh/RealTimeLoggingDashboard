import json
import threading
from queue import Queue
import jsonschema
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
import ssl
from datetime import datetime
from flask import Flask, request
import time

app = Flask(__name__)

# Define the standard JSON schema
standard_schema = {
   "type": "object",
   "properties": {
        "Id" : {"type": "string"},
        "date": {"type": "string", "format": "%d-%m-%Y"},
        "time": {"type": "string", "format": "%H:%M:%S"},
        "type" : {"type": "string"},
        "message" : {"type": "string"},
   },
   "required": ["Id", "date", "time","type","message"]
}
# Set up SSL context with Conduktor certificate
ssl_context = ssl.create_default_context()

# Set up connection properties

conf = {
    'bootstrap.servers':'',
  'sasl.mechanism':'',
  'security.protocol':'SASL_SSL',
  'sasl.username':'',
  'sasl.password':'',
  }
# Define the validation and transformation function
def standardize_log(log):
   try:
       jsonschema.validate(log, standard_schema)
       return log
   except jsonschema.ValidationError:
       # Transform the log to conform to the standard schema
       new_log = {
          "Id": log.get("Id"),
           "date": log.get("date"),
           "time": log.get("time"),
           "type": log.get("type"),
           "message": log.get("msg")
       }
       return new_log
def reverse_current_timestamp():
   # Get the current timestamp
   current_timestamp = datetime.now().timestamp()

   # Convert the timestamp to a datetime object
   dt = datetime.fromtimestamp(current_timestamp)

   # Format the datetime object in the desired format
   reversed_string = dt.strftime("%S:%M:%H%Y%m%d")

   # Remove non-numeric characters
   reversed_string = ''.join(filter(str.isdigit, reversed_string))

   return reversed_string
# Enhanced validation 
def standardize_json_log(json_log):
    try:
        log_data = json.loads(json_log)

        # Define a mapping of common log fields to standardized names
        field_mapping = {
            "Id":["Id","ID","App"],
            "timestamp": ["timestamp", "Data", "date"],
            "time": ["Time", "time", "TIME"],
            "message": ["message", "msg", "text"],
            "type": ["level", "severity", "type"]
        }

        # Initialize standardized log with empty values
        standardized_log = {field: None for field in field_mapping.keys()}

        # Iterate through field mappings and extract values if present
        for standard_field, possible_fields in field_mapping.items():
            for possible_field in possible_fields:
                if possible_field in log_data:
                    standardized_log[standard_field] = log_data[possible_field]
                    break

        return json.dumps(standardized_log)

    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {e}"
    

# Create a queue to store incoming logs
log_queue = Queue()

# Define a route that listens for incoming JSON logs
@app.route('/log', methods=['POST'])
def log_receiver():
   # Get the JSON log from the request body
   log = request.get_json()
   # Add the log to the queue
   #print(log)
   print("===========================================")
   log_queue.put(standardize_json_log(log))
   print(list(log_queue.queue))
#    print("===========================================")
   return 'Log received', 200

# Create a separate thread that acts as a Kafka producer and sends the logs to Kafka
def kafka_producer():
   # Define the Kafka producer configuration
   producer = Producer(conf)
   # Continuously send logs to Kafka
   while True:
       log = log_queue.get()
       serialized_message = json.dumps(log).encode('utf-8')
       log_dict = json.loads(log)
       toKafka_Key = log_dict["Id"]+reverse_current_timestamp()
       #print(serialized_message)
       # Record the start time
       start_time = time.time()
       producer.produce('Logs_Topic', key=toKafka_Key, value=serialized_message)
       end_time = time.time()
       producer.flush()
       print("Message was acknowledged by all in-sync replicas.")
       execution_time = end_time - start_time
       print(f"Execution time: {execution_time} seconds")

# Start the Flask application and the Kafka producer thread
if __name__ == '__main__':
   # Start the Kafka producer thread
   producer_thread = threading.Thread(target=kafka_producer)
   producer_thread.start()
   # Start the Flask application on port 8000
   app.run(port=8000)