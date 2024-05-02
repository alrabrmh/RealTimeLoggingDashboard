import threading
from queue import Queue
from confluent_kafka import Consumer, KafkaException
import sqlite3
import os
import json

# Function to consume logs_messages_tb from Kafka and add to queue
def consume_from_kafka():
    conf = {
    'bootstrap.servers':'',
    'sasl.mechanism':'',
    'group.id': '$GROUP_NAME',
    'auto.offset.reset': 'earliest',
    'security.protocol':'SASL_SSL',
    'sasl.username':'',
    'sasl.password':'',
    }

    consumer = Consumer(conf)
    consumer.subscribe(['Logs_Topic'])

    while True:
        try:
            msg = consumer.poll(timeout=1000)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    break

            key = msg.key().decode('utf-8')
            value = msg.value().decode('utf-8')
            print(json.loads(json.loads(value)))
            message_queue.put((key, value))

        except Exception as e:
            print(f"Error: {e}")

# Function to insert logs_messages_tb into SQLite database
def insert_to_database():
    if not os.path.exists(''):
        conn = sqlite3.connect('')
        c = conn.cursor()
        # Create a table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS logs_messages_tb (
                key TEXT,
                Id TEXT,
                dateLog TEXT,
                timeLog TEXT,
                message TEXT,
                messageType TEXT
            )
        ''')
        conn.commit()
        conn.close()

    while True:
        if message_queue.qsize() > 0:
            # print(message_queue.qsize())
            key, value = message_queue.get()
            # Deserialize JSON to a Python dictionary
            python_dict = json.loads(value)
            python_dict = json.loads(python_dict)

            conn = sqlite3.connect('')
            c = conn.cursor()
            # Insert data into the database
            c.execute('''
                INSERT INTO logs_messages_tb (key, Id, dateLog, timeLog, message, messageType)
                VALUES (?, ?, ?, ?, ? , ?)
            ''', (key, python_dict['Id'], python_dict['timestamp'], python_dict['time'], python_dict['message'], python_dict['type']))

            conn.commit()
            conn.close()
            print('Message Inserted Successfully !')
        else:
            pass

# Create a queue for passing logs_messages_tb between threads
message_queue = Queue()

# Create and start threads
kafka_thread = threading.Thread(target=consume_from_kafka)
database_thread = threading.Thread(target=insert_to_database)

kafka_thread.start()
database_thread.start()

# Keep the script running
try:
    while True:
        kafka_thread.join(timeout=1)
       # database_thread.join(timeout=1)
except KeyboardInterrupt:
    pass
