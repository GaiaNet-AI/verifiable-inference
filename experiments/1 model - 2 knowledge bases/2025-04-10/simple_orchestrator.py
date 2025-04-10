#!/usr/bin/env python3
"""
Simple script to run the experiment and then analyze the results.
"""

import os
from experiment_runner import Config, ExperimentRunner
from experiment_analyzer import ExperimentAnalyzer

def main():
    # Create a default configuration
    config = Config()
    
    # Get experiment mode from user
    print("\n=== Experiment Configuration ===")
    print("Select experiment mode:")
    print("1. Multiple Models (3 models, no knowledge base)")
    print("2. Knowledge Bases (1 model, 2 knowledge bases)")
    mode = input("Enter mode (1 or 2): ")
    
    if mode == "2":
        config.EXPERIMENT_MODE = "knowledge_bases"
        print("\nConfiguring Knowledge Base Experiment...")
        
        # Get node path
        node_path = input("Enter the path to the Gaia node: ").strip()
        if not os.path.exists(node_path):
            print(f"Warning: Path '{node_path}' does not exist")
            if input("Would you like to create it? (y/n): ").lower() == 'y':
                os.makedirs(node_path)
                print(f"Created directory: {node_path}")
        config.NODE_PATH = node_path
        
        # Get local-only flag
        local_only = input("\nRun in local-only mode? (y/n): ").lower().strip() == 'y'
        config.LOCAL_ONLY = local_only
        print(f"Local-only mode: {'enabled' if local_only else 'disabled'}")
        
        print("\n=== Configuration Summary ===")
        print(f"Model: {config.KB_MODEL} (port {config.KB_PORT})")
        print(f"Knowledge Base A (Paris): '{config.KB_URLS['kb_a']}'")
        print(f"Knowledge Base B (London): '{config.KB_URLS['kb_b']}'")
        print(f"Node Path: '{config.NODE_PATH}'")
        print(f"Local Only: {config.LOCAL_ONLY}")
        
        if input("\nProceed with experiment? (y/n): ").lower().strip() != 'y':
            print("Experiment cancelled.")
            return
    else:
        config.EXPERIMENT_MODE = "models"
        print("\nStarting experiment with the following models:")
        for model, url in config.MODELS.items():
            print(f"- {model}: {url}")
    
    # Run the experiment
    print("\nRunning experiment...")
    runner = ExperimentRunner(config)
    runner.run_sequential_experiment()
    
    # Save the results
    results_file = runner.save_raw_data()
    print(f"\nExperiment completed. Results saved to: {results_file}")
    
    # Run the analysis
    print("\nRunning analysis...")
    analyzer = ExperimentAnalyzer(results_file, len(config.QUESTIONS))
    report_path = analyzer.generate_report()
    
    print(f"\nAnalysis completed. Report saved to: {report_path}")
    print(f"Visualizations saved to: {analyzer.output_dir}")

if __name__ == "__main__":
    main()
