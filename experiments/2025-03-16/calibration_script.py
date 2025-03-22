#!/usr/bin/env python3
"""
Holistic Calibration Test for AI Model Experiment.

Uses a holistic binary search approach to find optimal settings by testing
combinations of parameters together rather than optimizing each in isolation.

    Starts with aggressive settings for all parameters
    If that fails, tries conservative settings for all parameters
    If that works, binary searches the middle ground for all parameters together
    Once we have a reliable configuration, optionally fine-tune individual parameters
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

# Initial aggressive settings (high performance)
AGGRESSIVE_SETTINGS = {
    "timeout": 5,      # seconds
    "concurrency": 25, # parallel workers
    "delay": 0.1       # seconds between requests
}

# Conservative settings (reliable but slower)
CONSERVATIVE_SETTINGS = {
    "timeout": 60,     # seconds
    "concurrency": 5,  # parallel workers
    "delay": 1.5       # seconds between requests
}

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
        print(f"COMPLETION ERROR: {str(e)} for URL {url}")
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
        print(f"EMBEDDING ERROR: {str(e)} for URL {url} with payload {json.dumps(payload)}")
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


def midpoint_settings(settings1, settings2):
    """Calculate the midpoint between two settings."""
    return {
        "timeout": (settings1["timeout"] + settings2["timeout"]) // 2,
        "concurrency": (settings1["concurrency"] + settings2["concurrency"]) // 2,
        "delay": (settings1["delay"] + settings2["delay"]) / 2
    }


def holistic_binary_search(models, questions, repeats, low_settings, high_settings):
    """Perform holistic binary search across all parameters together."""
    print("\n=== Starting holistic binary search for optimal settings ===")
    
    results = []
    
    # Test aggressive settings first
    print("\n--- Testing aggressive (high-performance) settings ---")
    aggressive_stats = test_settings(models, questions, low_settings, repeats)
    results.append(aggressive_stats)
    
    # If aggressive settings work well, we're done
    if aggressive_stats["success_rate"] >= SUCCESS_THRESHOLD:
        return aggressive_stats, results
    
    # Test conservative settings
    print("\n--- Testing conservative (reliable) settings ---")
    conservative_stats = test_settings(models, questions, high_settings, repeats)
    results.append(conservative_stats)
    
    # If conservative settings don't work, we need even more conservative settings
    if conservative_stats["success_rate"] < SUCCESS_THRESHOLD:
        print("\nWARNING: Even conservative settings don't reach the success threshold.")
        return conservative_stats, results
    
    # Binary search for the optimal middle ground
    low = low_settings
    high = high_settings
    
    # Keep tracking the best settings we've found
    best_settings = conservative_stats
    
    # Track which settings we've already tested to avoid duplicates
    tested_settings = {
        f"{low_settings['timeout']}-{low_settings['concurrency']}-{low_settings['delay']}",
        f"{high_settings['timeout']}-{high_settings['concurrency']}-{high_settings['delay']}"
    }
    
    # Perform binary search iterations (limit to avoid too many tests)
    for iteration in range(5):  # Maximum 5 iterations
        mid = midpoint_settings(low, high)
        
        # Skip if we've already tested these settings
        settings_key = f"{mid['timeout']}-{mid['concurrency']}-{mid['delay']}"
        if settings_key in tested_settings:
            break
        
        tested_settings.add(settings_key)
        
        print(f"\n--- Iteration {iteration+1}: Testing midpoint settings ---")
        mid_stats = test_settings(models, questions, mid, repeats)
        results.append(mid_stats)
        
        # If midpoint works, try more aggressive settings
        if mid_stats["success_rate"] >= SUCCESS_THRESHOLD:
            high = mid
            if mid_stats["success_rate"] > best_settings["success_rate"] or (
                mid_stats["success_rate"] == best_settings["success_rate"] and 
                mid_stats["tasks_per_second"] > best_settings["tasks_per_second"]
            ):
                best_settings = mid_stats
        else:
            # If midpoint doesn't work, try more conservative settings
            low = mid
    
    return best_settings, results


def main():
    """Run the holistic calibration test."""
    print("=== HOLISTIC MODEL PERFORMANCE CALIBRATION ===")
    print(f"Testing {len(MODELS)} models with {len(TEST_QUESTIONS)} questions, {REPEATS} repeats each")
    print(f"Total API calls per test: {len(MODELS) * len(TEST_QUESTIONS) * REPEATS * 2}")
    print(f"Success threshold: {SUCCESS_THRESHOLD}%\n")
    print("Aggressive settings:", AGGRESSIVE_SETTINGS)
    print("Conservative settings:", CONSERVATIVE_SETTINGS)
    
    if input("Ready to start calibration? (y/n): ").lower() != 'y':
        print("Calibration cancelled.")
        return
    
    # Perform holistic binary search
    best_settings, all_results = holistic_binary_search(
        MODELS, 
        TEST_QUESTIONS, 
        REPEATS, 
        AGGRESSIVE_SETTINGS, 
        CONSERVATIVE_SETTINGS
    )
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(all_results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_df.to_csv(f"holistic_calibration_{timestamp}.csv", index=False)
    
    # Find settings with highest success rate
    highest_success = max(all_results, key=lambda x: x["success_rate"])
    
    # Find fastest settings that meet the threshold
    threshold_results = [r for r in all_results if r["success_rate"] >= SUCCESS_THRESHOLD]
    if threshold_results:
        fastest_settings = max(threshold_results, key=lambda x: x["tasks_per_second"])
    else:
        fastest_settings = highest_success
    
    # Print recommended settings
    print("\n=== RECOMMENDED SETTINGS ===")
    print("\nMost reliable settings:")
    print(f"Timeout: {highest_success['timeout']} seconds")
    print(f"Concurrency: {highest_success['concurrency']} workers")
    print(f"Delay between requests: {highest_success['delay']} seconds")
    print(f"Success rate: {highest_success['success_rate']:.1f}%")
    print(f"Throughput: {highest_success['tasks_per_second']:.2f} tasks/second")
    
    if threshold_results and fastest_settings != highest_success:
        print("\nFastest reliable settings:")
        print(f"Timeout: {fastest_settings['timeout']} seconds")
        print(f"Concurrency: {fastest_settings['concurrency']} workers")
        print(f"Delay between requests: {fastest_settings['delay']} seconds")
        print(f"Success rate: {fastest_settings['success_rate']:.1f}%")
        print(f"Throughput: {fastest_settings['tasks_per_second']:.2f} tasks/second")
    
    # Generate settings for the main experiment script
    print("\n=== COPY-PASTE THESE SETTINGS INTO YOUR EXPERIMENT SCRIPT ===")
    print(f"""
    # Experiment settings optimized by holistic calibration
    TIMEOUT = {fastest_settings['timeout']}  # seconds
    MAX_WORKERS = {fastest_settings['concurrency']}
    REQUEST_DELAY = {fastest_settings['delay']}  # seconds between requests
    """)
    
    print(f"\nFull results saved to: holistic_calibration_{timestamp}.csv")


if __name__ == "__main__":
    main()