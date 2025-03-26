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
    
    print("Starting experiment with the following models:")
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
