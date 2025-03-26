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
    REQUEST_DELAY = 0.00625  # Delay between requests in seconds
    
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
    
    def run_sequential_experiment(self):
        """
        Run the experiment sequentially for each model with manual intervention.
        """
        # Reset results before starting
        self.results = {model: {} for model in self.config.MODELS.keys()}
        
        # Iterate through models in order
        for model_name, model_url in self.config.MODELS.items():
            print(f"\n===== Preparing to run experiments for {model_name} =====")
            print(f"Model URL: {model_url}")
            
            # Wait for user confirmation before starting this model
            input(f"Ensure {model_name} node is running. Press Enter when ready to start...")
            
            # Process all questions for this specific model
            model_results = {}
            for q_idx, question in enumerate(self.config.QUESTIONS):
                logger.info(f"Processing {model_name}, Q{q_idx+1}")
                
                question_results = []
                for repeat in range(self.config.NUM_REPEATS):
                    logger.info(f"  Repeat {repeat+1}/{self.config.NUM_REPEATS}")
                    
                    # Get completion
                    completion = self.make_completion_request(model_name, question)
                    if "error" in completion:
                        logger.error(f"Error in completion for Q{q_idx+1}, repeat {repeat+1}")
                        continue
                    
                    try:
                        response_text = completion["choices"][0]["message"]["content"]
                        
                        # Get embedding
                        embedding = self.get_embedding(model_name, response_text)
                        
                        # Store result for this repeat
                        question_results.append({
                            "repeat": repeat+1,
                            "response": response_text,
                            "embedding": embedding
                        })
                        
                        # Delay between requests
                        time.sleep(self.config.REQUEST_DELAY)
                    
                    except (KeyError, IndexError) as e:
                        logger.error(f"Error processing Q{q_idx+1}, repeat {repeat+1}: {str(e)}")
                
                # Store results for this question
                model_results[f"Q{q_idx+1}"] = question_results
            
            # Update overall results
            self.results[model_name] = model_results
            
            # Save intermediate results for this model
            self.save_model_results(model_name)
            
            print(f"\nCompleted experiments for {model_name}")
        
        # Analyze and save final results
        return self.analyze_results()
    
    def save_model_results(self, model_name):
        """
        Save results for a specific model.
        """
        output_dir = "./model_results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{model_name}_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.results[model_name], f, indent=2)
        
        logger.info(f"Saved results for {model_name} to {filename}")
    
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
            # Collect embeddings for statistical analysis
            all_embeddings = []
            for q_results in results.values():
                embeddings = [
                    np.array(item['embedding']) 
                    for item in q_results 
                    if item.get('embedding')
                ]
                all_embeddings.extend(embeddings)
            
            if all_embeddings:
                embeddings_array = np.array(all_embeddings)
                analysis["model_comparison"][model] = {
                    "avg_std_dev": np.std(embeddings_array, axis=0).mean(),
                    "num_total_embeddings": len(all_embeddings)
                }
        
        # Compare models per question
        for q_idx, question in enumerate(self.config.QUESTIONS):
            q_key = f"Q{q_idx+1}"
            analysis["per_question_analysis"][q_key] = {
                "question": question,
                "model_stats": {}
            }
            
            for model in self.config.MODELS.keys():
                # Collect embeddings for this model and question
                embeddings = [
                    np.array(item['embedding']) 
                    for item in self.results[model][q_key] 
                    if item.get('embedding')
                ]
                
                if embeddings:
                    embeddings_array = np.array(embeddings)
                    analysis["per_question_analysis"][q_key]["model_stats"][model] = {
                        "std_dev": np.std(embeddings_array, axis=0).mean(),
                        "num_responses": len(embeddings)
                    }
        
        return analysis
    
    def save_results(self, output_dir: str = "./results") -> str:
        """
        Save comprehensive experiment results.
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save analysis
        analysis = self.analyze_results()
        analysis_file = f"{output_dir}/analysis_{timestamp}.json"
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)
        
        # Print summary to console
        print("\n=== EXPERIMENT SUMMARY ===")
        print(f"Duration: {analysis['experiment_duration']}")
        print("\nModel comparison:")
        for model, stats in analysis["model_comparison"].items():
            print(f"  {model}: Avg std dev = {stats.get('avg_std_dev', 'N/A'):.4f}")
        
        logger.info(f"Results saved to {analysis_file}")
        return analysis_file

def main():
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
    
    logger.info("Starting sequential experiment execution")
    try:
        # Use sequential method 
        runner.run_sequential_experiment()
        
        print("\nExperiment completed successfully.")
        logger.info("Experiment completed successfully.")
    
    except KeyboardInterrupt:
        logger.warning("Experiment interrupted by user")
        print("\nExperiment interrupted.")
    
    except Exception as e:
        logger.error(f"Experiment failed: {str(e)}")
        print(f"\nExperiment failed: {str(e)}")
    
    total_time = datetime.now() - runner.start_time
    logger.info(f"Total experiment time: {total_time}")
    print(f"\nTotal experiment time: {total_time}")

if __name__ == "__main__":
    main()