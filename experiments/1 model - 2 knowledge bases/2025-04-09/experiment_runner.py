#!/usr/bin/env python3
"""
AI Model Consistency Experiment Runner

This script automates testing the consistency of responses across different
AI inference models.


This version rotates through all 20 questions once, then goes through them all a second time, and so on until it each question 25 times.
"""

import os
import json
import time
import numpy as np
import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Any, Optional
import logging
from pathlib import Path
import pickle
import warnings

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
    """Configuration parameters for the experiment."""
    # User-configurable experiment parameters
    TIMEOUT = 16  # API request timeout in seconds
    MAX_WORKERS = 15  # Concurrency (parallel workers)
    REQUEST_DELAY = 0.00625  # Delay between requests in seconds
    
    # No API key needed for local execution
    API_KEY = None
    
    # Experiment mode
    EXPERIMENT_MODE = "models"  # "models" or "knowledge_bases"
    
    # Model endpoints for "models" mode
    MODELS = {
        "llama-3-1-8b": "http://localhost:8080",
        "gemma-2-9b": "http://localhost:8081",
        "gemma-2-27b": "http://localhost:8082",
    }
    
    # Configuration for "knowledge_bases" mode
    KB_MODEL = "gemma-2-9b"
    KB_PORT = 8081
    KB_URLS = {
        "kb_a": "https://huggingface.co/datasets/gaianet/paris/resolve/main/paris_768_nomic-embed-text-v1.5-f16.snapshot.tar.gz",
        "kb_b": "https://huggingface.co/datasets/gaianet/london/resolve/main/london_768_nomic-embed-text-v1.5-f16.snapshot.tar.gz"
    }
    
    # Node configuration
    NODE_PATH = ""  # Path to the Gaia node
    LOCAL_ONLY = True  # Whether to run in local-only mode
    
    # Experiment parameters
    SYSTEM_PROMPT = "You are a helpful assistant."
    NUM_REPEATS = 25  # Number of times to repeat each question per model
    
    # Embedding model to use for semantic comparison
    EMBEDDING_MODEL = "gte-qwen2"
    
    # API request parameters
    TEMPERATURE = 0.7
    MAX_TOKENS = 1024
    TOP_P = 0.9
    
    # Auto-retry parameters for checking model availability
    CHECK_INTERVAL = 10  # Seconds between availability checks
    MAX_CHECK_ATTEMPTS = 30  # Maximum number of attempts (5 minutes at 10s intervals)
    
    # Questions for the models experiment (3 models, no knowledge base)
    MODEL_QUESTIONS = [
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
    
    # Questions for the knowledge base experiment (1 model, 2 knowledge bases)
    KB_QUESTIONS = [
        "What was the exact population of Greater London according to the 2011 census, and what was the population density per square mile mentioned in the London Knowledge Base?",
        "According to the London Knowledge Base, in which specific year did the Romans found Londinium, and what event in 61 AD led to its destruction?",
        "What specific polymath supervised the rebuilding of London after the Great Fire of 1666, and which architect's masterpiece cathedral was completed in 1708?",
        "Name all four World Heritage Sites in London as specifically listed in the London Knowledge Base, including the combined site that consists of three connected landmarks.",
        "In what precise year was Greater London divided into 32 London boroughs plus the City of London, and which previous administrative body was abolished in 1889 when the London County Council was created?",
        "What was the exact name of the defensive perimeter wall built during the English Civil War, how many people were involved in building it, and in what year was it leveled?",
        "What is the precise highest temperature ever recorded in London according to the Knowledge Base, on what exact date did it occur, and at which specific measuring station?",
        "Which two specific areas are identified as London's main financial districts in the Knowledge Base, and which one is described as having 'recently developed' into a financial hub?",
        "According to the 2021 census data in the Knowledge Base, what exact percentage of London's population was foreign-born, and what were the five largest single countries of origin in order?",
        "What specific governmental body is responsible for London's transport system according to the Knowledge Base, and what is the name of the functional arm through which it operates?",
        "How many visitors did the Louvre Museum receive in 2023?",
        "What is the name of the prefect who supervised the massive public works project that rebuilt Paris between 1853 and 1870?",
        "What happened to Paris during the Fronde civil war in the 17th century?",
        "What is the unemployment rate in Paris as reported in the 4th trimester of 2021?",
        "What percentage of Parisians earned less than €977 per month in 2012, according to the text?",
        "Which organization created the Vélib' bicycle sharing system in Paris and in what year?",
        "What is the name of the Paris stock exchange mentioned in the document?",
        "How many bridges did Philip Augustus build in Paris in the late 12th century?",
        "What percentage of Paris's salaried employees work in hotels and restaurants according to the document?",
        "What was the date when Paris was liberated from German occupation during World War II?"
    ]
    
    # Active questions based on experiment mode
    @property
    def QUESTIONS(self):
        return self.KB_QUESTIONS if self.EXPERIMENT_MODE == "knowledge_bases" else self.MODEL_QUESTIONS

class ExperimentRunner:
    """Main class to run consistency experiments across different models."""
    
    def __init__(self, config: Config):
        self.config = config
        self.start_time = datetime.now()
        
        # Initialize results structure based on experiment mode
        if config.EXPERIMENT_MODE == "models":
            self.results = {model: {} for model in config.MODELS.keys()}
        else:  # knowledge_bases mode
            self.results = {kb: {} for kb in config.KB_URLS.keys()}
        
        # Log experiment parameters for reference
        logger.info(f"Experiment started at {self.start_time}")
        logger.info(f"Experiment mode: {config.EXPERIMENT_MODE}")
        
        if config.EXPERIMENT_MODE == "models":
            logger.info(f"Testing models: {list(config.MODELS.keys())}")
        else:
            logger.info(f"Testing knowledge bases: {list(config.KB_URLS.keys())}")
            logger.info(f"Using model: {config.KB_MODEL}")
        
        logger.info(f"Number of questions: {len(config.QUESTIONS)}")
        logger.info(f"Repeats per question: {config.NUM_REPEATS}")
        logger.info(f"Timeout: {config.TIMEOUT} seconds")
        logger.info(f"Concurrency: {config.MAX_WORKERS} workers")
        logger.info(f"Delay between requests: {config.REQUEST_DELAY} seconds")
        
        if config.EXPERIMENT_MODE == "models":
            logger.info(f"Total API calls expected: {len(config.MODELS) * len(config.QUESTIONS) * config.NUM_REPEATS}")
        else:
            logger.info(f"Total API calls expected: {len(config.KB_URLS) * len(config.QUESTIONS) * config.NUM_REPEATS}")
    
    def check_model_availability(self, model: str) -> bool:
        """
        Check if a model's endpoints are available and responsive.
        Tests both completion and embedding endpoints.
        
        Args:
            model: Name of the model to check
            
        Returns:
            bool: True if both endpoints are responsive, False otherwise
        """
        base_url = self.config.MODELS.get(model)
        if not base_url:
            logger.error(f"Model {model} not found in configuration")
            return False
            
        # Check completion endpoint
        completion_url = f"{base_url}/v1/chat/completions"
        embedding_url = f"{base_url}/v1/embeddings"
        
        logger.info(f"Checking availability of {model} at {base_url}...")
        
        # Test completion endpoint
        try:
            completion_payload = {
                "messages": [
                    {"role": "system", "content": "Test message"},
                    {"role": "user", "content": "Hello, are you available?"}
                ],
                "max_tokens": 10
            }
            completion_response = requests.post(
                completion_url, 
                headers={"Content-Type": "application/json"},
                json=completion_payload,
                timeout=self.config.TIMEOUT
            )
            completion_available = completion_response.status_code == 200
            if not completion_available:
                logger.warning(f"Completion endpoint for {model} returned {completion_response.status_code}")
                return False
                
            # Test embedding endpoint
            embedding_payload = {
                "model": self.config.EMBEDDING_MODEL,
                "input": ["Test embedding"]
            }
            embedding_response = requests.post(
                embedding_url,
                headers={"Content-Type": "application/json"},
                json=embedding_payload,
                timeout=self.config.TIMEOUT
            )
            embedding_available = embedding_response.status_code == 200
            if not embedding_available:
                logger.warning(f"Embedding endpoint for {model} returned {embedding_response.status_code}")
                return False
                
            logger.info(f"Model {model} is available and responsive")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error checking availability for {model}: {str(e)}")
            return False
    
    def wait_for_model_availability(self, model: str) -> bool:
        """
        Wait until a model becomes available or max attempts are reached.
        
        Args:
            model: Name of the model to wait for
            
        Returns:
            bool: True if model becomes available, False if max attempts reached
        """
        print(f"\n===== Waiting for {model} to become available =====")
        logger.info(f"Waiting for {model} to become available...")
        
        for attempt in range(1, self.config.MAX_CHECK_ATTEMPTS + 1):
            if self.check_model_availability(model):
                print(f"\n{model} is now available!")
                return True
                
            print(f"Attempt {attempt}/{self.config.MAX_CHECK_ATTEMPTS}: {model} not available yet. "
                  f"Checking again in {self.config.CHECK_INTERVAL} seconds...")
            time.sleep(self.config.CHECK_INTERVAL)
            
        print(f"\nMax attempts reached. {model} is still not available.")
        logger.error(f"Max attempts reached. {model} is still not available.")
        return False
    
    def make_completion_request(self, model: str, question: str) -> Dict:
        """
        Send a request to the model's completion API endpoint.
        
        Args:
            model: Name of the model to query
            question: The question to ask the model
            
        Returns:
            Dict: The JSON response from the API
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
        
        Args:
            model: Name of the model to use for embedding
            text: The text to get embedding for
            
        Returns:
            List[float]: The embedding vector
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
        """Run the experiment sequentially through all models/knowledge bases and questions."""
        if self.config.EXPERIMENT_MODE == "models":
            return self._run_models_experiment()
        else:
            return self._run_knowledge_bases_experiment()
            
    def _run_models_experiment(self):
        """Run the experiment with different models."""
        # Reset results before starting
        self.results = {model: {} for model in self.config.MODELS.keys()}
        
        # Iterate through models in order
        for model_name, model_url in self.config.MODELS.items():
            print(f"\n===== Preparing to run experiments for {model_name} =====")
            print(f"Model URL: {model_url}")
            
            # Wait for model to become available
            if not self.wait_for_model_availability(model_name):
                print(f"Skipping {model_name} as it's not available")
                continue
            
            # Initialize model results structure
            model_results = {f"Q{q_idx+1}": [] for q_idx in range(len(self.config.QUESTIONS))}
            
            # Process questions in rotations
            for repeat in range(self.config.NUM_REPEATS):
                logger.info(f"Starting repeat {repeat+1}/{self.config.NUM_REPEATS} for all questions")
                
                for q_idx, question in enumerate(self.config.QUESTIONS):
                    q_key = f"Q{q_idx+1}"
                    logger.info(f"Processing {model_name}, {q_key}, repeat {repeat+1}")
                    
                    # Get completion
                    completion = self.make_completion_request(model_name, question)
                    if "error" in completion:
                        logger.error(f"Error in completion for {q_key}, repeat {repeat+1}")
                        continue
                    
                    try:
                        response_text = completion["choices"][0]["message"]["content"]
                        
                        # Get embedding
                        embedding = self.get_embedding(model_name, response_text)
                        
                        # Store result for this question and repeat
                        model_results[q_key].append({
                            "repeat": repeat+1,
                            "response": response_text,
                            "embedding": embedding
                        })
                        
                        # Delay between requests
                        time.sleep(self.config.REQUEST_DELAY)
                    
                    except (KeyError, IndexError) as e:
                        logger.error(f"Error processing {q_key}, repeat {repeat+1}: {str(e)}")
            
            # Update overall results
            self.results[model_name] = model_results
            
            # Save intermediate results for this model
            self.save_model_results(model_name)
            
            print(f"\nCompleted experiments for {model_name}")
        
        # Save raw experiment data for analysis
        self.save_raw_data()
        
        return self.results
        
    def _run_knowledge_bases_experiment(self):
        """Run the experiment with different knowledge bases."""
        # Reset results before starting
        self.results = {kb: {} for kb in self.config.KB_URLS.keys()}
        
        for kb_name, kb_url in self.config.KB_URLS.items():
            print(f"\n===== Preparing to run experiments for {kb_name} =====")
            print(f"Knowledge Base URL: {kb_url}")
            
            # Update config.json with the current knowledge base URL
            config_path = os.path.join(self.config.NODE_PATH, "config.json")
            with open(config_path, "r") as f:
                node_config = json.load(f)
            
            old_url = node_config.get("snapshot", "<none>")
            node_config["snapshot"] = kb_url
            
            print(f"\nUpdating config.json at {config_path}")
            print(f"  'snapshot': '{old_url}' -> '{kb_url}'")
            
            with open(config_path, "w") as f:
                json.dump(node_config, f, indent=2)
            
            # Initialize and start the node
            local_flag = "--local-only" if self.config.LOCAL_ONLY else ""
            print(f"\nInitializing node at {self.config.NODE_PATH}...")
            os.system(f"gaianet init --base {self.config.NODE_PATH}")
            
            print(f"\nStarting node{' in local-only mode' if self.config.LOCAL_ONLY else ''}...")
            os.system(f"gaianet start {local_flag} --base {self.config.NODE_PATH}")
            
            # Wait for node to start
            time.sleep(15)
            
            # Initialize results structure for this knowledge base
            kb_results = {f"Q{q_idx+1}": [] for q_idx in range(len(self.config.QUESTIONS))}
            
            # Process questions in rotations
            for repeat in range(self.config.NUM_REPEATS):
                logger.info(f"Starting repeat {repeat+1}/{self.config.NUM_REPEATS} for all questions")
                
                for q_idx, question in enumerate(self.config.QUESTIONS):
                    q_key = f"Q{q_idx+1}"
                    logger.info(f"Processing {kb_name}, {q_key}, repeat {repeat+1}")
                    
                    # Make request to fixed model port
                    url = f"http://localhost:{self.config.KB_PORT}/v1/chat/completions"
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
                        # Get completion
                        response = requests.post(
                            url,
                            headers={"Content-Type": "application/json"},
                            json=payload,
                            timeout=self.config.TIMEOUT
                        )
                        response.raise_for_status()
                        response_text = response.json()["choices"][0]["message"]["content"]
                        
                        # Get embedding
                        embedding_url = f"http://localhost:{self.config.KB_PORT}/v1/embeddings"
                        embedding_payload = {
                            "model": self.config.EMBEDDING_MODEL,
                            "input": [response_text]
                        }
                        
                        embedding_response = requests.post(
                            embedding_url,
                            headers={"Content-Type": "application/json"},
                            json=embedding_payload,
                            timeout=self.config.TIMEOUT
                        )
                        embedding_response.raise_for_status()
                        embedding = embedding_response.json()["data"][0]["embedding"]
                        
                        # Store result for this question and repeat
                        kb_results[q_key].append({
                            "repeat": repeat+1,
                            "response": response_text,
                            "embedding": embedding
                        })
                        
                        # Print progress
                        print(f"\rProcessed {kb_name}: Question {q_idx+1}/{len(self.config.QUESTIONS)} - "
                              f"Repeat {repeat+1}/{self.config.NUM_REPEATS}", end="")
                        
                        # Delay between requests
                        time.sleep(self.config.REQUEST_DELAY)
                        
                    except Exception as e:
                        logger.error(f"Error processing {kb_name}, {q_key}, repeat {repeat+1}: {str(e)}")
                        continue
                
                print()  # New line after progress indicator
            
            # Update overall results
            self.results[kb_name] = kb_results
            
            # Save intermediate results for this knowledge base
            self.save_model_results(kb_name)
            
            print(f"\nCompleted experiments for {kb_name}")
        
        # Save raw experiment data for analysis
        self.save_raw_data()
        
        return self.results
    
    def save_model_results(self, model_name):
        """
        Save results for a specific model.
        
        Args:
            model_name: Name of the model to save results for
        """
        output_dir = "./model_results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{model_name}_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.results[model_name], f, indent=2)
        
        logger.info(f"Saved results for {model_name} to {filename}")
    
    def save_raw_data(self):
        """
        Save the raw experiment data for analysis.
        Uses pickle to preserve arrays and ensure all data is captured.
        """
        output_dir = "./results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pickle_file = f"{output_dir}/raw_results_{timestamp}.pkl"
        json_file = f"{output_dir}/raw_results_{timestamp}.json"
        
        # Save as pickle for complete data preservation
        with open(pickle_file, "wb") as f:
            pickle.dump(self.results, f)
            
        # Save a JSON version for easier inspection (without embeddings)
        json_results = {}
        for model, model_data in self.results.items():
            json_results[model] = {}
            for q_key, q_data in model_data.items():
                json_results[model][q_key] = []
                for item in q_data:
                    # Exclude the embedding to make JSON viewable
                    json_results[model][q_key].append({
                        "repeat": item["repeat"],
                        "response": item["response"],
                        "has_embedding": len(item.get("embedding", [])) > 0
                    })
        
        with open(json_file, "w") as f:
            json.dump(json_results, f, indent=2)
            
        logger.info(f"Saved raw data to {pickle_file} and {json_file}")
        
        return pickle_file