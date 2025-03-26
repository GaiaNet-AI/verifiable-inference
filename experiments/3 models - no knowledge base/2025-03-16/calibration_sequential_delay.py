#!/usr/bin/env python3
import requests
import time
import numpy as np
import logging
from typing import Dict, List

class DelayCalibrator:
    def __init__(self, model_url: str, questions: List[str], repeats: int = 25):
        """
        Initialize delay calibrator for a single model endpoint.
        
        Args:
            model_url: Full URL of the model endpoint
            questions: List of test questions
            repeats: Number of times to repeat each question
        """
        self.model_url = model_url
        self.questions = questions
        self.repeats = repeats
        
        # Logging setup
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def make_completion_request(self, question: str, timeout: float = 16) -> Dict:
        """
        Send a completion request to the model.
        
        Args:
            question: Text of the question
            timeout: Request timeout in seconds
        
        Returns:
            API response or error dictionary
        """
        url = f"{self.model_url}/v1/chat/completions"
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
            "max_tokens": 150,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Completion request error: {e}")
            return {"error": str(e)}
    
    def get_embedding(self, text: str, timeout: float = 16) -> List[float]:
        """
        Get embedding for a given text.
        
        Args:
            text: Text to embed
            timeout: Request timeout in seconds
        
        Returns:
            Embedding vector or empty list
        """
        url = f"{self.model_url}/v1/embeddings"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gte-qwen2",
            "input": [text]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            return result["data"][0]["embedding"]
        except Exception as e:
            self.logger.error(f"Embedding request error: {e}")
            return []
    
    def calibrate_delay(self, 
                         min_delay: float = 0, 
                         max_delay: float = 0.8, 
                         success_threshold: float = 0.95) -> float:
        """
        Perform binary search to find optimal request delay.
        
        Args:
            min_delay: Minimum delay to test
            max_delay: Maximum delay to test
            success_threshold: Minimum acceptable success rate
        
        Returns:
            Optimal delay value
        """
        def test_delay(delay: float) -> Dict:
            """Test performance at a specific delay."""
            self.logger.info(f"\nTesting delay: {delay:.3f} seconds")
            
            model_results = {}
            for q_idx, question in enumerate(self.questions):
                question_results = []
                for repeat in range(self.repeats):
                    try:
                        # Get completion
                        completion = self.make_completion_request(question)
                        if "error" in completion:
                            continue
                        
                        response_text = completion["choices"][0]["message"]["content"]
                        
                        # Get embedding
                        embedding = self.get_embedding(response_text)
                        if not embedding:
                            continue
                        
                        # Store result
                        question_results.append({
                            "repeat": repeat + 1,
                            "response": response_text,
                            "embedding": embedding
                        })
                        
                        # Delay between requests
                        time.sleep(delay)
                    
                    except Exception as e:
                        self.logger.error(f"Error processing question {q_idx}: {e}")
                
                model_results[f"Q{q_idx+1}"] = question_results
            
            # Calculate success rate
            total_tasks = len(self.questions) * self.repeats
            successful_tasks = sum(
                len([r for r in q_results if r.get('embedding')])
                for q_results in model_results.values()
            )
            
            success_rate = successful_tasks / total_tasks
            self.logger.info(f"Success Rate: {success_rate:.2%}")
            
            return {
                "success_rate": success_rate,
                "delay": delay
            }
        
        # Binary search
        low, high = min_delay, max_delay
        best_working = None
        
        while high - low > 0.01:  # Precision of 0.01 seconds
            mid = (low + high) / 2
            
            result = test_delay(mid)
            
            if result['success_rate'] >= success_threshold:
                # This delay works, try lower
                best_working = result
                high = mid
            else:
                # This delay doesn't work, try higher
                low = mid
        
        # Final result
        optimal_delay = best_working['delay'] if best_working else max_delay
        
        self.logger.info("\n=== DELAY CALIBRATION COMPLETE ===")
        self.logger.info(f"Optimal Delay: {optimal_delay:.3f} seconds")
        self.logger.info(f"Success Rate: {best_working['success_rate']:.2%}")
        
        return optimal_delay

def main():
    # Example usage
    model_url = "http://localhost:8080"  # Replace with actual model URL
    questions = [
        "What year did the Apollo 11 mission land on the moon?",
        "Who wrote Pride and Prejudice?",
        # Add more questions as needed
    ]
    
    calibrator = DelayCalibrator(model_url, questions)
    optimal_delay = calibrator.calibrate_delay()
    print(f"Recommended delay: {optimal_delay} seconds")

if __name__ == "__main__":
    main()