#!/usr/bin/env python3
"""
LLM Response Analysis

Analyzes consistency and statistical separation of LLM model responses.

Usage:
    1. Process a folder of JSON result files:
       python3 response_analysis.py --folder ./model_consistency_results --output-dir ./analysis_results
    
    2. Process specific JSON files:
       python3 response_analysis.py --files file1.json file2.json file3.json --output-dir ./analysis_results
    
    3. Debug mode (more verbose output):
       python3 response_analysis.py --folder ./model_consistency_results --debug
    
The script:
    - Computes average and standard deviation of embeddings for each model's responses
    - Determines if models are statistically separated (mean distance > standard deviation)
    - Generates visualizations comparing model consistency
    - Outputs analysis results as JSON files
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import argparse
import sys

def load_experiment_data(file_path: str) -> Dict[str, Any]:
    """Load experiment data from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_embeddings(data: Dict[str, Any]) -> Dict[str, np.ndarray]:
    """Extract embeddings from the data structure."""
    result = {}
    
    if "embeddings" in data:
        # Direct embeddings structure
        for question, embeddings in data["embeddings"].items():
            result[question] = np.array(embeddings)
    
    return result

def compute_statistics(embeddings_dict: Dict[str, np.ndarray]) -> Dict[str, Dict[str, Any]]:
    """Compute statistics for each question's embeddings."""
    results = {}
    
    all_mean_stds = []
    min_std = float('inf')
    max_std = 0
    
    for question, embeddings_array in embeddings_dict.items():
        # Calculate mean and standard deviation
        mean_embedding = np.mean(embeddings_array, axis=0)
        std_embedding = np.std(embeddings_array, axis=0)
        mean_std = float(np.mean(std_embedding))
        
        # Update min/max values
        min_std = min(min_std, mean_std)
        max_std = max(max_std, mean_std)
        all_mean_stds.append(mean_std)
        
        # Store statistics
        results[question] = {
            "mean_embedding": mean_embedding.tolist(),
            "std_embedding": std_embedding.tolist(),
            "mean_std": mean_std
        }
    
    # Overall statistics across all questions
    if all_mean_stds:
        results["overall"] = {
            "mean_std_across_questions": float(np.mean(all_mean_stds)),
            "min_std": float(min_std),
            "max_std": float(max_std)
        }
    else:
        results["overall"] = {
            "mean_std_across_questions": 0,
            "min_std": 0,
            "max_std": 0
        }
    
    return results

def are_models_separated(model_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Determine if the average points for any two models are separated by 
    at least the standard deviation.
    """
    model_names = list(model_stats.keys())
    separation_results = {model1: {} for model1 in model_names}
    
    for i, model1 in enumerate(model_names):
        for model2 in model_names[i+1:]:
            questions = [q for q in model_stats[model1].keys() if q != "overall" and q in model_stats[model2]]
            
            model_separated = True
            question_separation = {}
            
            for question in questions:
                mean1 = np.array(model_stats[model1][question]["mean_embedding"])
                mean2 = np.array(model_stats[model2][question]["mean_embedding"])
                std1 = np.array(model_stats[model1][question]["std_embedding"])
                std2 = np.array(model_stats[model2][question]["std_embedding"])
                
                # Calculate Euclidean distance between means
                distance = np.linalg.norm(mean1 - mean2)
                
                # Average of standard deviations
                avg_std = (np.mean(std1) + np.mean(std2)) / 2
                
                # Check if distance is greater than average std
                is_separated = distance > avg_std
                question_separation[question] = int(is_separated)  # Convert bool to int
                
                if not is_separated:
                    model_separated = False
            
            separation_results[model1][model2] = {
                "overall_separated": int(model_separated),  # Convert bool to int
                "by_question": question_separation
            }
            separation_results[model2][model1] = separation_results[model1][model2]
    
    return separation_results

def visualize_model_consistency(model_stats: Dict[str, Dict[str, Any]], output_dir: str = "./"):
    """Generate visualizations for model consistency."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Extract mean standard deviations for each model
    models = list(model_stats.keys())
    mean_stds = [stats["overall"]["mean_std_across_questions"] for stats in model_stats.values()]
    
    # Plot overall consistency comparison
    plt.figure(figsize=(10, 6))
    bars = plt.bar(models, mean_stds)
    plt.xlabel('Model')
    plt.ylabel('Mean Standard Deviation')
    plt.title('Consistency Comparison Across Models (Lower is more consistent)')
    plt.xticks(rotation=45)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.0001,
                 f'{height:.4f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path / "model_consistency_comparison.png")
    
    # Create question-level consistency heatmap
    question_stds = {}
    all_questions = set()
    
    for model, stats in model_stats.items():
        questions = [q for q in stats.keys() if q != "overall"]
        all_questions.update(questions)
        question_stds[model] = {q: stats[q]["mean_std"] for q in questions}
    
    if all_questions:
        all_questions = sorted(list(all_questions))
        df_data = []
        
        for model in models:
            row = [question_stds[model].get(q, np.nan) for q in all_questions]
            df_data.append(row)
        
        df = pd.DataFrame(df_data, index=models, columns=all_questions)
        
        plt.figure(figsize=(max(len(all_questions) * 0.5, 10), max(len(models) * 0.5, 6)))
        heatmap = plt.pcolor(df, cmap='viridis')
        plt.colorbar(heatmap, label='Standard Deviation')
        plt.yticks(np.arange(0.5, len(df.index)), df.index)
        plt.xticks(np.arange(0.5, len(df.columns)), df.columns, rotation=90)
        plt.title('Standard Deviation by Question and Model')
        plt.tight_layout()
        plt.savefig(output_path / "question_model_heatmap.png")

def process_model_file(file_path: str, debug: bool = False) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]]]:
    """Process a single model's results file."""
    print(f"Processing {file_path}")
    data = load_experiment_data(file_path)
    
    if debug:
        print(f"File contains keys: {list(data.keys())}")
    
    # Extract embeddings
    embeddings_dict = extract_embeddings(data)
    
    if debug:
        print(f"Found embeddings for {len(embeddings_dict)} questions")
        
    # Extract responses if available
    responses_dict = {}
    if "responses" in data:
        responses_dict = data["responses"]
        if debug:
            print(f"Found responses for {len(responses_dict)} questions")
    
    # Compute statistics
    stats = compute_statistics(embeddings_dict)
    
    return stats, responses_dict

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Analyze LLM response consistency and model separation.')
    parser.add_argument('--folder', type=str, help='Path to folder containing experiment result JSON files')
    parser.add_argument('--files', type=str, nargs='*', help='Path(s) to individual experiment results JSON file(s)')
    parser.add_argument('--output-dir', type=str, default='./results', help='Directory to save analysis results and visualizations')
    parser.add_argument('--debug', action='store_true', help='Print debug information')
    args = parser.parse_args()
    
    # Collect file paths to process
    file_paths = []
    
    # Add individual files if specified
    if args.files:
        file_paths.extend(args.files)
    
    # Add all JSON files from folder if specified
    if args.folder:
        folder_path = Path(args.folder)
        if folder_path.exists() and folder_path.is_dir():
            json_files = list(folder_path.glob('*.json'))
            file_paths.extend(str(f) for f in json_files)
            print(f"Found {len(json_files)} JSON files in {args.folder}")
        else:
            print(f"Warning: Folder {args.folder} does not exist or is not a directory")
    
    if not file_paths:
        print("Error: No files to process. Specify --folder or --files.")
        return
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Process each model file
    all_model_stats = {}
    all_model_responses = {}
    
    for file_path in file_paths:
        try:
            # Extract model name from filename
            model_name = Path(file_path).stem.split('_')[0]
            
            # Process the model file
            stats, responses = process_model_file(file_path, args.debug)
            
            if "overall" in stats:
                all_model_stats[model_name] = stats
                all_model_responses[model_name] = responses
                
                # Save individual model statistics
                with open(Path(args.output_dir) / f"{model_name}_stats.json", "w") as f:
                    json.dump(stats, f, indent=2)
            else:
                print(f"Warning: No valid statistics computed for {model_name}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            if args.debug:
                import traceback
                traceback.print_exc()
    
    # Check if we have at least two models to compare
    if len(all_model_stats) >= 2:
        # Determine if models are separated
        separation = are_models_separated(all_model_stats)
        
        # Save combined results
        with open(Path(args.output_dir) / "model_separation.json", "w") as f:
            json.dump(separation, f, indent=2)
        
        # Generate visualizations
        visualize_model_consistency(all_model_stats, args.output_dir)
        
        # Print summary
        print("\nModel consistency (mean standard deviation across questions):")
        for model, stats in all_model_stats.items():
            print(f"{model}: {stats['overall']['mean_std_across_questions']:.6f}")
        
        print("\nModel separation results:")
        for model1, comparisons in separation.items():
            for model2, result in comparisons.items():
                if model1 < model2:  # Avoid printing duplicates
                    is_separated = result["overall_separated"] == 1
                    print(f"{model1} vs {model2}: {'Separated' if is_separated else 'Not separated'}")
    else:
        print("Need at least two models to perform separation analysis.")

if __name__ == "__main__":
    main()