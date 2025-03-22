#!/usr/bin/env python3
"""
Manual Calibration Script for AI Model Experiment
"""

import requests
import time
import concurrent.futures
from datetime import datetime
import statistics
import pandas as pd

MODELS = {
    "llama-3-1-8b": "http://localhost:8080",
    "gemma-2-9b": "http://localhost:8081",
    "gemma-2-27b": "http://localhost:8082",
}

TEST_QUESTIONS = [
    "What year did the Apollo 11 mission land on the moon?",
    "Who wrote Pride and Prejudice?",
    "What is the capital of Japan?"
]

REPEATS = 3

def make_completion_request(model_url, question, timeout):
    url = f"{model_url}/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        latency = time.time() - start_time
        return {
            "success": True,
            "latency": latency,
            "response": result["choices"][0]["message"]["content"] if "choices" in result else None
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "success": False,
            "latency": latency,
            "error": str(e)
        }

def make_embedding_request(model_url, text, timeout):
    url = f"{model_url}/v1/embeddings"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gte-qwen2",
        "input": [text]
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        latency = time.time() - start_time
        embedding_size = len(result["data"][0]["embedding"]) if "data" in result else 0
        return {
            "success": True,
            "latency": latency,
            "embedding_size": embedding_size
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "success": False,
            "latency": latency,
            "error": str(e)
        }

def process_single_request(model_name, model_url, question, timeout, delay):
    completion_result = make_completion_request(model_url, question, timeout)
    
    embedding_result = None
    if completion_result["success"] and completion_result["response"]:
        time.sleep(delay)
        embedding_result = make_embedding_request(model_url, completion_result["response"], timeout)
    
    return {
        "model": model_name,
        "question": question,
        "completion": completion_result,
        "embedding": embedding_result
    }

def test_settings(models, questions, timeout, concurrency, delay, repeats):
    print(f"\n=== Testing with timeout={timeout}s, concurrency={concurrency}, delay={delay}s ===")
    start_time = datetime.now()
    
    tasks = []
    for _ in range(repeats):
        for model_name, model_url in models.items():
            for question in questions:
                tasks.append((model_name, model_url, question))
    
    results = []
    success_count = 0
    total_tasks = len(tasks)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {}
        for model_name, model_url, question in tasks:
            future = executor.submit(
                process_single_request, 
                model_name, 
                model_url, 
                question, 
                timeout, 
                delay
            )
            futures[future] = (model_name, model_url, question)
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                
                if result["completion"]["success"]:
                    success_count += 0.5
                    if result["embedding"] and result["embedding"]["success"]:
                        success_count += 0.5
                
                completed += 1
                print(f"\rProgress: {completed}/{total_tasks} tasks completed", end="")
            except Exception as e:
                model_name, _, question = futures[future]
                print(f"\nError in task for model {model_name}, question: {question[:30]}...: {str(e)}")
    
    total_time = (datetime.now() - start_time).total_seconds()
    success_rate = (success_count / total_tasks) * 100
    
    completion_latencies = [r["completion"]["latency"] for r in results if r["completion"]["success"]]
    embedding_latencies = [r["embedding"]["latency"] for r in results if r["embedding"] and r["embedding"]["success"]]
    
    stats = {
        "timeout": timeout,
        "concurrency": concurrency,
        "delay": delay,
        "total_tasks": total_tasks,
        "total_time": total_time,
        "success_rate": success_rate,
        "tasks_per_second": total_tasks / total_time if total_time > 0 else 0,
        "avg_completion_latency": statistics.mean(completion_latencies) if completion_latencies else 0,
        "max_completion_latency": max(completion_latencies) if completion_latencies else 0,
        "avg_embedding_latency": statistics.mean(embedding_latencies) if embedding_latencies else 0,
        "completion_success_rate": (len(completion_latencies) / total_tasks) * 100,
        "embedding_success_rate": (len(embedding_latencies) / total_tasks) * 100 if embedding_latencies else 0
    }
    
    print(f"\nResults for timeout={timeout}s, concurrency={concurrency}, delay={delay}s:")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Completion success: {stats['completion_success_rate']:.1f}%")
    print(f"Embedding success: {stats['embedding_success_rate']:.1f}%")
    print(f"Total time: {total_time:.1f}s")
    print(f"Tasks per second: {stats['tasks_per_second']:.2f}")
    
    return stats

def main():
    print("=== MANUAL CALIBRATION SCRIPT ===")
    
    # Get user inputs
    timeout = float(input("Enter timeout (seconds): "))
    concurrency = int(input("Enter concurrency (number of workers): "))
    delay = float(input("Enter delay between requests (seconds): "))
    
    # Run the test
    test_settings(MODELS, TEST_QUESTIONS, timeout, concurrency, delay, REPEATS)

if __name__ == "__main__":
    main()