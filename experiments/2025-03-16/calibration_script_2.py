#!/usr/bin/env python3
"""
Binary Search Calibration for AI Model Experiment.

This script optimizes delay first to reduce total experiment time.
"""

import requests
import time
import json
import concurrent.futures
from datetime import datetime
import statistics
import pandas as pd

# Configuration
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
    "delay": 0.8       # seconds between requests
}

# Parameter ranges for binary search
TIMEOUT_RANGE = {"min": 1, "max": 16}  # seconds
CONCURRENCY_RANGE = {"min": 15, "max": 50}  # parallel workers
DELAY_RANGE = {"min": 0.1, "max": 0.8}  # seconds

# System prompt for all requests
SYSTEM_PROMPT = "You are a helpful assistant."


def make_completion_request(model_url, question, timeout):
    """Make a completion request to the model."""
    url = f"{model_url}/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
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
    concurrency = settings.get("concurrency", 15)  # Default to 15 if not provided
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


def binary_search_delay(models, questions, repeats, base_settings, min_val, max_val):
    """
    Use binary search to find minimal delay that maintains performance.
    
    Focuses on reducing delay from current value, keeping timeout constant.
    """
    print("\n=== Binary search for minimal delay ===")
    results = []
    
    # Start with conservative (current) max delay to establish baseline
    current_settings = base_settings.copy()
    current_settings["delay"] = max_val
    max_stats = test_settings(models, questions, current_settings, repeats)
    results.append(max_stats)
    
    if max_stats["success_rate"] < SUCCESS_THRESHOLD:
        print(f"\nCurrent delay ({max_val}s) doesn't meet success threshold.")
        return max_stats, results
    
    # Try the minimum aggressive delay
    current_settings["delay"] = min_val
    min_stats = test_settings(models, questions, current_settings, repeats)
    results.append(min_stats)
    
    # Binary search to find minimal working delay
    low = min_val
    high = max_val
    best_working = max_stats
    
    tested_values = {min_val, max_val}
    tolerance = 0.05  # 0.05 second precision
    
    while high - low > tolerance:
        mid = (low + high) / 2
        
        # Avoid retesting values
        mid_rounded = round(mid * 100) / 100
        if mid_rounded in tested_values:
            break
            
        tested_values.add(mid_rounded)
        current_settings["delay"] = mid_rounded
        mid_stats = test_settings(models, questions, current_settings, repeats)
        results.append(mid_stats)
        
        if mid_stats["success_rate"] >= SUCCESS_THRESHOLD:
            low = mid  # This works, try more aggressive (lower) value
            best_working = mid_stats
        else:
            high = mid  # This doesn't work, use higher delay
    
    print(f"\nOptimal minimal delay: {best_working['delay']} seconds")
    return best_working, results


def main():
    """Run the binary search calibration test."""
    print("=== BINARY SEARCH CALIBRATION ===")
    print(f"Testing {len(MODELS)} models with {len(TEST_QUESTIONS)} questions, {REPEATS} repeats each")
    print(f"Success threshold: {SUCCESS_THRESHOLD}%\n")
    print("Baseline settings from holistic calibration:", BASELINE_SETTINGS)
    
    if input("\nReady to start calibration? (y/n): ").lower() != 'y':
        print("Calibration cancelled.")
        return
    
    all_results = []
    current_best_settings = BASELINE_SETTINGS.copy()
    
    # Focus on optimizing delay first
    print("\n--- PHASE 1: Optimizing Delay ---")
    delay_best, delay_results = binary_search_delay(
        MODELS, TEST_QUESTIONS, REPEATS, 
        current_best_settings,
        DELAY_RANGE["min"],
        DELAY_RANGE["max"]
    )
    all_results.extend(delay_results)
    current_best_settings["delay"] = delay_best["delay"]
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(all_results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_df.to_csv(f"binary_search_calibration_{timestamp}.csv", index=False)
    
    # Print final optimized settings
    print("\n=== OPTIMIZED SETTINGS ===")
    print(f"Delay between requests: {current_best_settings['delay']} seconds")
    print(f"Timeout (unchanged): {current_best_settings['timeout']} seconds")
    
    final_stats = delay_best
    if final_stats:
        print(f"Success rate: {final_stats['success_rate']:.1f}%")
        print(f"Throughput: {final_stats['tasks_per_second']:.2f} tasks/second")
    
    # Generate settings for the main experiment script
    print("\n=== COPY-PASTE THESE SETTINGS INTO YOUR EXPERIMENT SCRIPT ===")
    print(f"""
    # Experiment settings optimized by binary search calibration
    TIMEOUT = {current_best_settings['timeout']}  # seconds (unchanged)
    REQUEST_DELAY = {current_best_settings['delay']}  # seconds between requests
    """)
    
    print(f"\nFull results saved to: binary_search_calibration_{timestamp}.csv")


if __name__ == "__main__":
    main()