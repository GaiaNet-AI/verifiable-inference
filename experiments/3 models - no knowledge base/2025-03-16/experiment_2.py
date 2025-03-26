#!/usr/bin/env python3
"""
AI Model Consistency Experiment

This script automates testing the consistency of responses across different
AI inference models running locally.
"""

import os
import json
import time
import numpy as np
import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Any
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("experiment_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    # User-configurable experiment parameters
    TIMEOUT = 16  # API request timeout in seconds
    MAX_WORKERS = 15  # Concurrency (parallel workers)
    REQUEST_DELAY = 0.8  # Delay between requests in seconds
    
    # No API key needed for local execution
    API_KEY = None
    
    # Model endpoints
    MODELS = {
        "llama-3-1-8b": "http://localhost:8080",
        "gemma-2-9b": "http://localhost:8081",
        "gemma-2-27b": "http://localhost:8082",
    }
    
    # Experiment parameters
    SYSTEM_PROMPT = "You are a helpful assistant."
    NUM_REPEATS = 25  # Number of times to repeat each question per model
    
    # Embedding model to use for semantic comparison
    EMBEDDING_MODEL = "gte-qwen2"
    
    # API request parameters
    TEMPERATURE = 0.7
    MAX_TOKENS = 150
    TOP_P = 0.9
    
    # Factual questions for the experiment
    QUESTIONS = [
        "What year did the Apollo 11 mission land on the moon?",
        "Who wrote Pride and Prejudice?",
        "What is the capital of Japan?",
        "What is the chemical formula for water?",
        "Who painted the Mona Lisa?",
        "What is the largest planet in our solar system?",
        "In what year did World War II end?",
        "What is the speed of light in a vacuum?",
        "Who discovered penicillin?",
        "What is the boiling point of water at sea level in Celsius?",
        "Who was the first woman to win a Nobel Prize?",
        "What is the capital of Australia?",
        "Who wrote 'Romeo and Juliet'?",
        "What is the atomic number of oxygen?",
        "Who was the first person to step on the moon?",
        "What is the circumference of Earth?",
        "In which year was the Declaration of Independence signed?",
        "What is the tallest mountain on Earth?",
        "Who developed the theory of relativity?",
        "What is the largest ocean on Earth?"
    ]

class ExperimentRunner:
    def __init__(self, config: Config):
        self.config = config
        # Initialize results structure for storing responses and statistics
        self.results = {model: {} for model in config.MODELS.keys()}
        self.start_time = datetime.now()
        
        # Log experiment parameters for reference
        logger.info(f"Experiment started at {self.start_time}")
        logger.info(f"Testing models: {list(config.MODELS.keys())}")
        logger.info(f"Number of questions: {len(config.QUESTIONS)}")
        logger.info(f"Repeats per question: {config.NUM_REPEATS}")
        logger.info(f"Timeout: {config.TIMEOUT} seconds")
        logger.info(f"Concurrency: {config.MAX_WORKERS} workers")
        logger.info(f"Delay between requests: {config.REQUEST_DELAY} seconds")
        logger.info(f"Total API calls expected: {len(config.MODELS) * len(config.QUESTIONS) * config.NUM_REPEATS}")
    
    def make_completion_request(self, model: str, question: str) -> Dict:
        """
        Send a request to the model's completion API endpoint.
        """
        url = f"{self.config.MODELS[model]}/v1/chat/completions"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [
                {"role": "system", "content": self.config.SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            "temperature": self.config.TEMPERATURE,
            "max_tokens": self.config.MAX_TOKENS,
            "top_p": self.config.TOP_P
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making completion request to {model}: {str(e)}")
            return {"error": str(e)}
    
    def get_embedding(self, model: str, text: str) -> List[float]:
        """
        Get embedding vector for a text response.
        """
        url = f"{self.config.MODELS[model]}/v1/embeddings"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config.EMBEDDING_MODEL,
            "input": [text]
        }
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.TIMEOUT)
            response.raise_for_status()
            result = response.json()
            return result["data"][0]["embedding"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting embedding from {model}: {str(e)}")
            return []
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response format from embedding API: {str(e)}")
            return []
    
    def process_question_for_model(self, model: str, question: str, q_idx: int) -> Dict:
        """
        Process a single question for a specific model with multiple repeats.
        """
        responses = []
        embeddings = []
        
        for i in range(self.config.NUM_REPEATS):
            logger.info(f"Processing {model}, Q{q_idx+1}, repeat {i+1}/{self.config.NUM_REPEATS}")
            
            # Get completion
            completion = self.make_completion_request(model, question)
            if "error" in completion:
                logger.error(f"Skipping this repeat due to API error")
                continue
                
            try:
                response_text = completion["choices"][0]["message"]["content"]
                responses.append(response_text)
                
                # Get embedding for this response
                embedding = self.get_embedding(model, response_text)
                if embedding:
                    embeddings.append(embedding)
                
                # Delay between requests
                time.sleep(self.config.REQUEST_DELAY)
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error extracting response: {str(e)}")
                continue
        
        # Compute statistics if we have embeddings
        stats = {}
        if embeddings:
            embeddings_array = np.array(embeddings)
            stats = {
                # Calculate mean standard deviation across all dimensions
                "std_dev": np.std(embeddings_array, axis=0).mean(),
                "median_embedding": np.median(embeddings_array, axis=0).tolist(),
                "num_responses": len(responses),
                "num_embeddings": len(embeddings)
            }
        
        return {
            "question": question,
            "responses": responses,
            "stats": stats
        }
    
    def run_experiment_parallel(self) -> Dict:
        """
        Run the experiment with parallel processing.
        """
        tasks = []
        
        for model in self.config.MODELS.keys():
            for q_idx, question in enumerate(self.config.QUESTIONS):
                tasks.append((model, question, q_idx))
        
        logger.info(f"Created {len(tasks)} tasks for parallel execution")
        
        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            futures = {executor.submit(self.process_question_for_model, model, question, q_idx): (model, q_idx) 
                      for model, question, q_idx in tasks}
            
            for future in futures:
                model, q_idx = futures[future]
                try:
                    result = future.result()
                    self.results[model][f"Q{q_idx+1}"] = result
                except Exception as e:
                    logger.error(f"Error in parallel task for {model}, Q{q_idx+1}: {str(e)}")
        
        return self.analyze_results()
    
    # [Rest of the methods remain the same as in the original script]
    
    def analyze_results(self) -> Dict:
        """
        Analyze the experiment results to quantify consistency across models.
        """
        logger.info("Analyzing experiment results...")
        analysis = {
            "experiment_duration": str(datetime.now() - self.start_time),
            "model_comparison": {},
            "per_question_analysis": {}
        }
        
        # Calculate overall statistics per model
        for model, results in self.results.items():
            std_devs = [q_result["stats"].get("std_dev", 0) for q_result in results.values() 
                       if "stats" in q_result and "std_dev" in q_result["stats"]]
            
            if std_devs:
                analysis["model_comparison"][model] = {
                    "avg_std_dev": np.mean(std_devs),
                    "min_std_dev": np.min(std_devs),
                    "max_std_dev": np.max(std_devs)
                }
        
        # Compare models per question
        for q_idx, question in enumerate(self.config.QUESTIONS):
            q_key = f"Q{q_idx+1}"
            analysis["per_question_analysis"][q_key] = {
                "question": question,
                "model_stats": {}
            }
            
            for model in self.config.MODELS.keys():
                if q_key in self.results[model] and "stats" in self.results[model][q_key]:
                    analysis["per_question_analysis"][q_key]["model_stats"][model] = {
                        "std_dev": self.results[model][q_key]["stats"].get("std_dev", 0),
                        "num_responses": self.results[model][q_key]["stats"].get("num_responses", 0)
                    }
        
        # Find questions with high deviation across models
        high_deviation_questions = []
        for q_key, q_analysis in analysis["per_question_analysis"].items():
            std_devs = [stats.get("std_dev", 0) for model, stats in q_analysis["model_stats"].items()]
            if std_devs and max(std_devs) > np.mean(std_devs) * 1.5:  # 50% higher than mean
                high_deviation_questions.append({
                    "question_key": q_key,
                    "question": q_analysis["question"],
                    "max_std_dev": max(std_devs),
                    "avg_std_dev": np.mean(std_devs)
                })
        
        analysis["high_deviation_questions"] = high_deviation_questions
        
        return analysis
    
    def save_results(self, output_dir: str = "./results") -> str:
        """
        Save experiment results to files for later analysis.
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Save raw results (excluding full embeddings to save space)
        compact_results = {model: {} for model in self.results.keys()}
        for model, model_results in self.results.items():
            for q_key, q_result in model_results.items():
                compact_results[model][q_key] = {
                    "question": q_result["question"],
                    "num_responses": len(q_result["responses"]),
                    "stats": q_result["stats"],
                    # Store first 3 responses as examples
                    "sample_responses": q_result["responses"][:3] if "responses" in q_result else []
                }
        
        results_file = f"{output_dir}/results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(compact_results, f, indent=2)
        
        # Save analysis
        analysis = self.analyze_results()
        with open(f"{output_dir}/analysis_{timestamp}.json", "w") as f:
            json.dump(analysis, f, indent=2)
        
        # Generate CSV summary
        summary_data = []
        for q_idx, question in enumerate(self.config.QUESTIONS):
            q_key = f"Q{q_idx+1}"
            row = {"Question": question}
            
            for model in self.config.MODELS.keys():
                if q_key in self.results[model] and "stats" in self.results[model][q_key]:
                    row[f"{model}_std_dev"] = self.results[model][q_key]["stats"].get("std_dev", 0)
                    row[f"{model}_responses"] = self.results[model][q_key]["stats"].get("num_responses", 0)
            
            summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        df.to_csv(f"{output_dir}/summary_{timestamp}.csv", index=False)
        
        logger.info(f"Results saved to {output_dir}")
        
        # Print summary to console
        print("\n=== EXPERIMENT SUMMARY ===")
        print(f"Duration: {analysis['experiment_duration']}")
        print("\nModel comparison:")
        for model, stats in analysis["model_comparison"].items():
            print(f"  {model}: Avg std dev = {stats['avg_std_dev']:.4f}")
        
        if analysis["high_deviation_questions"]:
            print("\nQuestions with high deviation:")
            for q in analysis["high_deviation_questions"]:
                print(f"  {q['question_key']}: {q['question'][:50]}... (max_std={q['max_std_dev']:.4f})")
        
        return results_file
    
def main():
    """Main function to run the experiment."""
    config = Config()
    
    # Explicitly allow user to modify key parameters
    print("\n===== AI MODEL CONSISTENCY EXPERIMENT =====")
    print("Default Settings:")
    print(f"Timeout: {config.TIMEOUT} seconds")
    print(f"Concurrency: {config.MAX_WORKERS} workers")
    print(f"Delay between requests: {config.REQUEST_DELAY} seconds")
    
    modify = input("Would you like to modify these settings? (y/n): ").lower()
    if modify == 'y':
        config.TIMEOUT = float(input("Enter timeout (seconds): "))
        config.MAX_WORKERS = int(input("Enter concurrency (number of workers): "))
        config.REQUEST_DELAY = float(input("Enter delay between requests (seconds): "))
    
    print(f"\nModels to test: {', '.join(config.MODELS.keys())}")
    print(f"Number of questions: {len(config.QUESTIONS)}")
    
    config.NUM_REPEATS = int(input("Repeats per question: "))
    
    if input("Ready to start the experiment? (y/n): ").lower() != 'y':
        print("Experiment cancelled.")
        return
    
    runner = ExperimentRunner(config)
    
    logger.info("Starting experiment execution")
    try:
        # Display progress updates in a separate thread
        import threading
        
        stop_status_thread = False
        
        def status_updater():
            nonlocal stop_status_thread
            while not stop_status_thread:
                total_tasks = len(config.MODELS) * len(config.QUESTIONS)
                completed_tasks = sum(1 for model in runner.results for q in runner.results[model] if runner.results[model][q])
                print(f"\rProgress: {completed_tasks}/{total_tasks} tasks completed ({(completed_tasks/total_tasks)*100:.1f}%)", end="")
                time.sleep(15)
        
        status_thread = threading.Thread(target=status_updater)
        status_thread.daemon = True
        status_thread.start()
        
        # Run the experiment
        runner.run_experiment_parallel()
        
        # Stop status thread
        stop_status_thread = True
        status_thread.join(timeout=1)
        
        results_path = runner.save_results()
        print(f"\nExperiment completed successfully.")
        logger.info(f"Experiment completed successfully. Results saved to {results_path}")
    except KeyboardInterrupt:
        logger.warning("Experiment interrupted by user")
        print("\n\nExperiment interrupted. Saving partial results...")
        runner.save_results(output_dir="./partial_results")
        print("Partial results saved to ./partial_results")
    except Exception as e:
        logger.error(f"Experiment failed: {str(e)}")
        print(f"\n\nExperiment failed: {str(e)}")
        print("Saving partial results...")
        try:
            runner.save_results(output_dir="./partial_results")
            print("Partial results saved to ./partial_results")
        except:
            print("Failed to save partial results")
    
    total_time = datetime.now() - runner.start_time
    logger.info(f"Total experiment time: {total_time}")
    print(f"\nTotal experiment time: {total_time}")

if __name__ == "__main__":
    main()