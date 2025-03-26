#!/usr/bin/env python3
"""
Model Consistency Experiment

Generates responses per model and analyzes embedding consistency.
"""

import os
import json
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

class ModelConsistencyExperiment:
    def __init__(self, models: Dict[str, str], questions: List[str], repeats: int = 25):
        """
        Initialize experiment parameters.
        
        Args:
            models: Dictionary of model names and their endpoints
            questions: List of test questions
            repeats: Number of times to repeat each question
        """
        self.models = models
        self.questions = questions
        self.repeats = repeats
        self.results_dir = "./model_consistency_results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def make_completion_request(self, model_url: str, question: str) -> str:
        """
        Send completion request to a model.
        """
        url = f"{model_url}/v1/chat/completions"
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9
        }
        
        response = requests.post(url, headers={"accept": "application/json", "Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    def get_embedding(self, model_url: str, text: str) -> List[float]:
        """
        Generate embedding for a given text.
        """
        url = f"{model_url}/v1/embeddings"
        payload = {"model": "gte-qwen2", "input": [text]}
        
        response = requests.post(url, headers={"accept": "application/json", "Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    
    def run_experiment(self):
        """
        Execute the full model consistency experiment.
        """
        experiment_results = {}
        
        for model_name, model_url in self.models.items():
            # Prompt user to confirm the model is ready
            input(f"\n🚀 Ready to test {model_name} on {model_url}? Press ENTER to start...")
            
            print(f"\n🔍 Running experiment for {model_name}...")
            model_results = {"responses": {}, "embeddings": {}, "stats": {}}
            
            for q_idx, question in enumerate(self.questions, 1):
                print(f"   ➡️ Processing Q{q_idx}/{len(self.questions)}: {question}")
                
                question_responses = []
                question_embeddings = []
                
                for repeat in range(self.repeats):
                    print(f"      🔄 Iteration {repeat + 1}/{self.repeats}")
                    
                    # Get completion response
                    response = self.make_completion_request(model_url, question)
                    question_responses.append(response)
                    
                    # Get embedding
                    embedding = self.get_embedding(model_url, response)
                    question_embeddings.append(embedding)
                    
                    time.sleep(0.5)  # Brief delay
                
                model_results["responses"][f"Q{q_idx}"] = question_responses
                model_results["embeddings"][f"Q{q_idx}"] = question_embeddings
            
            model_results["stats"] = self.compute_model_statistics(model_results["embeddings"])
            experiment_results[model_name] = model_results
            
            # Save results
            self.save_model_results(model_name, model_results)
        
        self.save_experiment_results(experiment_results)
        return experiment_results
    
    def compute_model_statistics(self, embeddings: Dict[str, List[List[float]]]) -> Dict:
        """
        Compute statistical measures for embeddings.
        """
        stats = {}
        
        for question, question_embeddings in embeddings.items():
            embeddings_array = np.array(question_embeddings)
            mean_embedding = np.mean(embeddings_array, axis=0)
            std_embedding = np.std(embeddings_array, axis=0)
            
            stats[question] = {
                "mean_embedding": mean_embedding.tolist(),
                "std_embedding": std_embedding.tolist(),
                "mean_std": float(np.mean(std_embedding))
            }
        
        overall_means = [stats[q]["mean_std"] for q in stats]
        stats["overall"] = {
            "mean_std_across_questions": float(np.mean(overall_means)),
            "min_std": float(np.min(overall_means)),
            "max_std": float(np.max(overall_means))
        }
        
        return stats
    
    def save_model_results(self, model_name: str, model_results: Dict):
        """
        Save results for a specific model.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_dir}/{model_name}_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(model_results, f, indent=2)
        
        print(f"✅ Saved results for {model_name} to {filename}")
    
    def save_experiment_results(self, experiment_results: Dict):
        """
        Save full experiment results.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_dir}/full_experiment_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(experiment_results, f, indent=2)
        
        print("\n📊 Full experiment results saved.")
    
    def analyze_model_differences(self, experiment_results: Dict):
        """
        Compare embedding differences between models.
        """
        print("\n=== MODEL EMBEDDING COMPARISON ===")
        model_names = list(experiment_results.keys())
        
        for i in range(len(model_names)):
            for j in range(i+1, len(model_names)):
                model1, model2 = model_names[i], model_names[j]
                print(f"\n🔬 Comparing {model1} and {model2}...")
                
                significant_differences = []
                
                for q_key in experiment_results[model1]["stats"]:
                    if q_key == "overall":
                        continue
                    
                    m1_mean = np.array(experiment_results[model1]["stats"][q_key]["mean_embedding"])
                    m2_mean = np.array(experiment_results[model2]["stats"][q_key]["mean_embedding"])
                    m1_std = np.array(experiment_results[model1]["stats"][q_key]["std_embedding"])
                    m2_std = np.array(experiment_results[model2]["stats"][q_key]["std_embedding"])
                    
                    max_std = np.maximum(m1_std, m2_std)
                    diff = np.abs(m1_mean - m2_mean)
                    
                    if np.all(diff > max_std):
                        significant_differences.append(q_key)
                
                print(f"   📉 Significant differences found in {len(significant_differences)} questions.")

def main():
    models = {
        "llama-3-1-8b": "http://localhost:8080",
        "gemma-2-9b": "http://localhost:8081",
        "gemma-2-27b": "http://localhost:8082"
    }
    
    questions = [
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
    
    experiment = ModelConsistencyExperiment(models, questions)
    experiment.run_experiment()

if __name__ == "__main__":
    main()