import time
from kafka import KafkaProducer
import sys

KAFKA_BROKER = "kafka:9092"
TIMEOUT = 60  # segundos

start = time.time()
while True:
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
        producer.close()
        print("Kafka is available!")
        break
    except Exception as e:
        if time.time() - start > TIMEOUT:
            print("Timeout waiting for Kafka broker.", file=sys.stderr)
            sys.exit(1)
        print("Waiting for Kafka broker to be available...")
        time.sleep(2)