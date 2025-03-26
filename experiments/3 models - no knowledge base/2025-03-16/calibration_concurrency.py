#!/usr/bin/env python3
"""
Binary Search Calibration for AI Model Experiment.

This script incrementally increases concurrency until first failure.
"""

import requests
import time
import json
import concurrent.futures
from datetime import datetime
import statistics
import pandas as pd

# Configuration (same as previous script)
MODELS = {
    "llama-3-1-8b": "http://localhost:8080",
    "gemma-2-9b": "http://localhost:8081",
    "gemma-2-27b": "http://localhost:8082",
}

# Test questions - a small subset of factual questions
TEST_QUESTIONS = [
    "What year did the Apollo 11 mission land on the moon?",
    "Who wrote Pride and Prejudice?",
    "What is the capital of Japan?"
]

# Number of repeats per question
REPEATS = 3

# Success threshold - what percentage of requests should succeed
SUCCESS_THRESHOLD = 95.0  # 95% success rate

# Starting point from holistic calibration
BASELINE_SETTINGS = {
    "timeout": 16,     # seconds
    "concurrency": 15, # parallel workers
    "delay": 0.76      # seconds between requests
}

def make_completion_request(model_url, question, timeout):
    """Make a completion request to the model."""
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
    """Make an embedding request to the model."""
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
    """Process a single question-response-embedding sequence."""
    # Make completion request
    completion_result = make_completion_request(model_url, question, timeout)
    
    # If completion successful, get embedding
    embedding_result = None
    if completion_result["success"] and completion_result["response"]:
        # Apply delay before next request
        time.sleep(delay)
        embedding_result = make_embedding_request(model_url, completion_result["response"], timeout)
    
    return {
        "model": model_name,
        "question": question,
        "completion": completion_result,
        "embedding": embedding_result
    }


def test_settings(models, questions, settings, repeats):
    """Test a specific combination of settings."""
    timeout = settings["timeout"]
    concurrency = settings["concurrency"]
    delay = settings["delay"]
    
    print(f"\n=== Testing with timeout={timeout}s, concurrency={concurrency}, delay={delay}s ===")
    start_time = datetime.now()
    
    # Build the task list
    tasks = []
    for _ in range(repeats):
        for model_name, model_url in models.items():
            for question in questions:
                tasks.append((model_name, model_url, question))
    
    results = []
    success_count = 0
    total_tasks = len(tasks)
    
    # Run tasks with specified concurrency
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
                
                # Count successful completions and embeddings
                if result["completion"]["success"]:
                    success_count += 0.5  # Half point for completion
                    if result["embedding"] and result["embedding"]["success"]:
                        success_count += 0.5  # Half point for embedding
                
                # Print progress
                completed += 1
                print(f"\rProgress: {completed}/{total_tasks} tasks completed", end="")
            except Exception as e:
                model_name, _, question = futures[future]
                print(f"\nError in task for model {model_name}, question: {question[:30]}...: {str(e)}")
                raise  # Re-raise to trigger error handling
    
    total_time = (datetime.now() - start_time).total_seconds()
    success_rate = (success_count / total_tasks) * 100
    
    # Calculate completion and embedding latencies
    completion_latencies = [r["completion"]["latency"] for r in results if r["completion"]["success"]]
    embedding_latencies = [r["embedding"]["latency"] for r in results if r["embedding"] and r["embedding"]["success"]]
    
    # Calculate statistics
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


def incrementally_increase_concurrency(models, questions, repeats, base_settings, increment=5, max_concurrency=100):
    """
    Incrementally increase concurrency until first failure.
    
    Args:
        models: Dictionary of model endpoints
        questions: List of test questions
        repeats: Number of times to repeat each question
        base_settings: Dictionary with baseline settings
        increment: Number of workers to add each iteration
        max_concurrency: Maximum concurrency to test
    """
    print("=== Incrementally Increasing Concurrency ===")
    
    current_settings = base_settings.copy()
    results = []
    
    while current_settings["concurrency"] <= max_concurrency:
        try:
            stats = test_settings(models, questions, current_settings, repeats)
            results.append(stats)
            
            # Prepare for next iteration
            current_settings["concurrency"] += increment
            
        except Exception as e:
            print(f"\nError encountered at concurrency {current_settings['concurrency']}")
            print(f"Error details: {e}")
            break
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_df.to_csv(f"concurrency_increment_{timestamp}.csv", index=False)
    
    # Find the highest working concurrency
    working_results = [r for r in results if r["success_rate"] >= 95.0]
    if working_results:
        best_result = max(working_results, key=lambda x: x["tasks_per_second"])
        print("\n=== BEST WORKING CONFIGURATION ===")
        print(f"Concurrency: {best_result['concurrency']}")
        print(f"Tasks per second: {best_result['tasks_per_second']:.2f}")
        print(f"Success rate: {best_result['success_rate']:.1f}%")
    
    print(f"\nFull results saved to: concurrency_increment_{timestamp}.csv")
    
    return results


def main():
    """Run the concurrency increment test."""
    print("=== CONCURRENCY INCREMENT CALIBRATION ===")
    print(f"Testing {len(MODELS)} models with {len(TEST_QUESTIONS)} questions, {REPEATS} repeats each")
    
    # Run the incremental concurrency test
    incrementally_increase_concurrency(
        MODELS, 
        TEST_QUESTIONS, 
        REPEATS, 
        BASELINE_SETTINGS
    )


if __name__ == "__main__":
    main()