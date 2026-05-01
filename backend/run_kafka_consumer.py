#!/usr/bin/env python3
"""
Kafka Consumer Entry Point

Run this script to start the gamification event consumer.
Usage: python run_kafka_consumer.py
"""
import sys
import os

if __name__ == "__main__":
    try:
        from kafka_consumer import start_consumer
        start_consumer()
    except ImportError as e:
        print(f"Error: Failed to import kafka_consumer: {e}")
        print("Make sure kafka-python is installed: pip install kafka-python")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
