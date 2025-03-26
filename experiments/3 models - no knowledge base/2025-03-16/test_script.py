#!/usr/bin/env python3
"""
Test script to verify connectivity to all three model endpoints.
This helps diagnose connectivity issues before running the full experiment.
"""

import requests
import json
import traceback
import time

# Configure the models to test
MODELS = {
    "llama-3-1-8b": "http://localhost:8080",
    "gemma-2-9b": "http://localhost:8081",
    "gemma-2-27b": "http://localhost:8082",
}

TIMEOUT = 60  # Timeout in seconds

def test_completion(model_name, model_url):
    """Test a completion request for a specific model"""
    url = f"{model_url}/v1/chat/completions"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9
    }
    
    print(f"\n=== Testing chat completion for {model_name} ===")
    print(f"Sending request to {url}")
    print(f"Using timeout: {TIMEOUT} seconds")
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start_time
        
        print("\nSUCCESS! Received response:")
        print(f"Status code: {response.status_code}")
        
        # Print the response text
        if "choices" in result and len(result["choices"]) > 0:
            print("\nModel response:")
            print(result["choices"][0]["message"]["content"])
        else:
            print("\nWARNING: Unexpected response format:")
            print(json.dumps(result, indent=2))
        
        # Print details about timing
        print(f"Request took {elapsed:.2f} seconds")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"\nERROR: Request timed out after {TIMEOUT} seconds")
        print("Consider increasing the timeout value or checking if the model is running correctly.")
        return False
    
    except requests.exceptions.ConnectionError as e:
        print(f"\nERROR: Connection error: {str(e)}")
        print("Check if the model server is running and the URL is correct.")
        return False
        
    except requests.exceptions.HTTPError as e:
        print(f"\nERROR: HTTP Error: {str(e)}")
        try:
            error_details = e.response.json()
            print(f"Error details: {json.dumps(error_details, indent=2)}")
        except:
            print(f"Response content: {e.response.text}")
        return False
        
    except Exception as e:
        print(f"\nERROR: Request failed: {str(e)}")
        print(traceback.format_exc())
        return False

def test_embedding(model_name, model_url):
    """Test an embedding request for a specific model"""
    url = f"{model_url}/v1/embeddings"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gte-qwen2",
        "input": ["Hello world"]
    }
    
    print(f"\n=== Testing embedding for {model_name} ===")
    print(f"Sending request to {url}")
    print(f"Using timeout: {TIMEOUT} seconds")
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start_time
        
        print("\nSUCCESS! Received embedding response:")
        print(f"Status code: {response.status_code}")
        
        # Print the embedding dimensions
        if "data" in result and len(result["data"]) > 0:
            embedding = result["data"][0]["embedding"]
            print(f"Embedding dimensions: {len(embedding)}")
            print(f"First few values: {embedding[:5]}...")
        else:
            print("\nWARNING: Unexpected embedding response format:")
            print(json.dumps(result, indent=2))
        
        print(f"Request took {elapsed:.2f} seconds")
        return True
        
    except requests.exceptions.Timeout:
        print(f"\nERROR: Embedding request timed out after {TIMEOUT} seconds")
        return False
    
    except requests.exceptions.ConnectionError as e:
        print(f"\nERROR: Embedding connection error: {str(e)}")
        return False
        
    except requests.exceptions.HTTPError as e:
        print(f"\nERROR: Embedding HTTP Error: {str(e)}")
        try:
            error_details = e.response.json()
            print(f"Error details: {json.dumps(error_details, indent=2)}")
        except:
            print(f"Response content: {e.response.text}")
        return False
        
    except Exception as e:
        print(f"\nERROR: Embedding request failed: {str(e)}")
        print(traceback.format_exc())
        return False

def main():
    """Test completion and embedding for all models"""
    print("=== MODEL CONNECTIVITY TEST ===")
    print(f"Testing {len(MODELS)} models with {TIMEOUT}s timeout")
    
    results = {model: {"completion": False, "embedding": False} for model in MODELS}
    
    for model_name, model_url in MODELS.items():
        print(f"\n\n{'='*50}")
        print(f"TESTING MODEL: {model_name}")
        print(f"URL: {model_url}")
        print(f"{'='*50}")
        
        # Test completion
        completion_success = test_completion(model_name, model_url)
        results[model_name]["completion"] = completion_success
        
        # Test embedding only if completion succeeds
        if completion_success:
            embedding_success = test_embedding(model_name, model_url)
            results[model_name]["embedding"] = embedding_success
    
    # Print summary
    print("\n\n" + "="*60)
    print("SUMMARY OF TEST RESULTS")
    print("="*60)
    
    all_success = True
    for model_name in MODELS:
        completion_status = "✅ PASSED" if results[model_name]["completion"] else "❌ FAILED"
        embedding_status = "✅ PASSED" if results[model_name]["embedding"] else "❌ FAILED"
        
        print(f"{model_name}:")
        print(f"  Completion API: {completion_status}")
        print(f"  Embedding API:  {embedding_status}")
        
        if not (results[model_name]["completion"] and results[model_name]["embedding"]):
            all_success = False
    
    print("\n" + "="*60)
    if all_success:
        print("🎉 ALL TESTS PASSED! You can now run the full experiment.")
    else:
        print("⚠️ SOME TESTS FAILED! Please fix the issues before running the full experiment.")
        print("\nSuggestions:")
        print("1. Verify all model servers are running")
        print("2. Check if the API endpoints are correctly configured")
        print("3. Check if the embedding model 'gte-qwen2' is available on all servers")
        print("4. Examine the model server logs for errors")

if __name__ == "__main__":
    main()