#!/usr/bin/env python3
"""
AI Model Consistency Experiment Analyzer

This script analyzes and visualizes the results from the AI model consistency
experiment, focusing on Euclidean distances between mean embeddings.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging
from pathlib import Path
from scipy.spatial.distance import euclidean
import itertools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analysis_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExperimentAnalyzer:
    """Analyzes results from the model consistency experiment."""
    
    def __init__(self, results_file: str, num_questions: int = 20):
        """
        Initialize the analyzer with experiment results.
        
        Args:
            results_file: Path to the pickle file containing raw results
            num_questions: Number of questions in the experiment
        """
        self.results_file = results_file
        self.num_questions = num_questions
        self.results = self._load_results()
        self.models = list(self.results.keys())
        self.questions = [f"Q{i+1}" for i in range(num_questions)]
        
        # Create output directory
        self.output_dir = f"./analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Analyzing results from {results_file}")
        logger.info(f"Models: {self.models}")
        logger.info(f"Questions: {len(self.questions)}")
        
    def _load_results(self) -> Dict:
        """
        Load results from pickle file.
        
        Returns:
            Dict: The experiment results
        """
        try:
            with open(self.results_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading results: {str(e)}")
            raise
    
    def calculate_mean_embedding(self, model: str, question: str) -> np.ndarray:
        """
        Calculate the mean embedding for a model-question pair.
        
        Args:
            model: The model name
            question: The question key (e.g., "Q1")
            
        Returns:
            np.ndarray: The mean embedding vector
        """
        question_data = self.results[model].get(question, [])
        embeddings = [np.array(item["embedding"]) for item in question_data if item.get("embedding")]
        
        if not embeddings:
            logger.warning(f"No embeddings found for {model}, {question}")
            return np.array([])
            
        # Stack embeddings and calculate mean
        return np.mean(np.vstack(embeddings), axis=0)
    
    def calculate_all_mean_embeddings(self) -> Dict[Tuple[str, str], np.ndarray]:
        """
        Calculate mean embeddings for all model-question pairs.
        
        Returns:
            Dict: Dictionary mapping (model, question) tuples to mean embeddings
        """
        mean_embeddings = {}
        
        for model in self.models:
            for question in self.questions:
                mean_emb = self.calculate_mean_embedding(model, question)
                
                if len(mean_emb) > 0:
                    mean_embeddings[(model, question)] = mean_emb
                
        return mean_embeddings
    
    def calculate_euclidean_distances(self) -> pd.DataFrame:
        """
        Calculate Euclidean distances between mean embeddings of all model pairs
        for each question.
        
        Returns:
            pd.DataFrame: DataFrame with distances between model pairs for each question
        """
        # Calculate mean embeddings for all model-question pairs
        mean_embeddings = self.calculate_all_mean_embeddings()
        
        # Initialize results container
        distances = []
        
        # Calculate distances for each question
        for question in self.questions:
            # Get all model pairs
            model_pairs = list(itertools.combinations(self.models, 2))
            
            for model1, model2 in model_pairs:
                # Get mean embeddings
                emb1 = mean_embeddings.get((model1, question))
                emb2 = mean_embeddings.get((model2, question))
                
                if emb1 is not None and emb2 is not None and len(emb1) > 0 and len(emb2) > 0:
                    # Calculate Euclidean distance
                    distance = euclidean(emb1, emb2)
                    
                    # Store result
                    distances.append({
                        "question": question,
                        "model1": model1,
                        "model2": model2,
                        "distance": distance
                    })
        
        # Convert to DataFrame
        df = pd.DataFrame(distances)
        
        return df
    
    def calculate_mean_stddev(self, model: str, question: str) -> float:
        """
        Calculate mean standard deviation across dimensions for a model-question pair.
        Formula: σ_avg = (1/d) ∑(j=1 to d) σ_j
        
        Args:
            model: The model name
            question: The question key (e.g., "Q1")
            
        Returns:
            float: Mean standard deviation
        """
        question_data = self.results[model].get(question, [])
        embeddings = [np.array(item["embedding"]) for item in question_data if item.get("embedding")]
        
        if not embeddings:
            logger.warning(f"No embeddings found for {model}, {question}")
            return 0.0
            
        # Stack embeddings and calculate standard deviation for each dimension
        stacked = np.vstack(embeddings)
        std_per_dim = np.std(stacked, axis=0)
        
        # Mean of standard deviations
        return np.mean(std_per_dim)
    
    def calculate_rms_scatter(self, model: str, question: str) -> float:
        """
        Calculate root-mean-square scatter for a model-question pair.
        Formula: σ_total = √(1/d ∑(j=1 to d) σ²_j)
        
        Args:
            model: The model name
            question: The question key (e.g., "Q1")
            
        Returns:
            float: Root-mean-square scatter
        """
        question_data = self.results[model].get(question, [])
        embeddings = [np.array(item["embedding"]) for item in question_data if item.get("embedding")]
        
        if not embeddings:
            logger.warning(f"No embeddings found for {model}, {question}")
            return 0.0
            
        # Stack embeddings and calculate standard deviation for each dimension
        stacked = np.vstack(embeddings)
        std_per_dim = np.std(stacked, axis=0)
        
        # Root-mean-square of standard deviations (sqrt of mean of squares)
        return np.sqrt(np.mean(np.square(std_per_dim)))
    
    def calculate_consistency_metrics(self) -> pd.DataFrame:
        """
        Calculate both consistency metrics for all model-question pairs.
        
        Returns:
            pd.DataFrame: DataFrame with consistency metrics
        """
        metrics = []
        
        for model in self.models:
            for question in self.questions:
                mean_stddev = self.calculate_mean_stddev(model, question)
                rms_scatter = self.calculate_rms_scatter(model, question)
                
                metrics.append({
                    "model": model,
                    "question": question,
                    "mean_stddev": mean_stddev,
                    "rms_scatter": rms_scatter
                })
        
        return pd.DataFrame(metrics)
    
    def plot_distance_matrix(self, save_path: Optional[str] = None):
        """
        Plot a heatmap of distances between model pairs for each question.
        
        Args:
            save_path: Optional path to save the plot
        """
        # Calculate distances
        distances_df = self.calculate_euclidean_distances()
        
        # Pivot to create matrix
        pivot_df = distances_df.pivot_table(
            index="question", 
            columns=["model1", "model2"], 
            values="distance"
        )
        
        # Create figure
        plt.figure(figsize=(14, 10))
        sns.heatmap(
            pivot_df, 
            annot=True, 
            cmap="viridis", 
            linewidths=0.5,
            fmt=".3f"
        )
        plt.title("Euclidean Distances Between Model Mean Embeddings")
        plt.xlabel("Model Pairs")
        plt.ylabel("Questions")
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Saved distance matrix plot to {save_path}")
        
        plt.close()
    
    def plot_consistency_metrics(self, save_dir: Optional[str] = None):
        """
        Plot consistency metrics for all models.
        
        Args:
            save_dir: Optional directory to save the plots
        """
        # Calculate metrics
        metrics_df = self.calculate_consistency_metrics()
        
        # Plot mean standard deviation
        plt.figure(figsize=(14, 8))
        sns.boxplot(x="model", y="mean_stddev", data=metrics_df)
        plt.title("Mean Standard Deviation Across Dimensions")
        plt.xlabel("Model")
        plt.ylabel("Mean Standard Deviation")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_dir:
            mean_stddev_path = os.path.join(save_dir, "mean_stddev.png")
            plt.savefig(mean_stddev_path)
            logger.info(f"Saved mean standard deviation plot to {mean_stddev_path}")
        
        plt.close()
        
        # Plot RMS scatter
        plt.figure(figsize=(14, 8))
        sns.boxplot(x="model", y="rms_scatter", data=metrics_df)
        plt.title("Root-Mean-Square Scatter")
        plt.xlabel("Model")
        plt.ylabel("RMS Scatter")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_dir:
            rms_scatter_path = os.path.join(save_dir, "rms_scatter.png")
            plt.savefig(rms_scatter_path)
            logger.info(f"Saved RMS scatter plot to {rms_scatter_path}")
        
        plt.close()
    
    def generate_report(self) -> str:
        """
        Generate a detailed report of the analysis.
        
        Returns:
            str: Path to the generated report
        """
        # Calculate metrics
        distances_df = self.calculate_euclidean_distances()
        metrics_df = self.calculate_consistency_metrics()
        
        # Create plots
        self.plot_distance_matrix(os.path.join(self.output_dir, "distance_matrix.png"))
        self.plot_consistency_metrics(self.output_dir)
        
        # Calculate summary statistics
        avg_distances = distances_df.groupby(["model1", "model2"])["distance"].mean().reset_index()
        avg_distances = avg_distances.sort_values("distance")
        
        model_metrics = metrics_df.groupby("model").agg({
            "mean_stddev": ["mean", "std", "min", "max"],
            "rms_scatter": ["mean", "std", "min", "max"]
        }).reset_index()
        
        # Generate report content
        report_content = "# AI Model Consistency Experiment Report\n\n"
        report_content += f"Analysis generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report_content += "## Experiment Overview\n\n"
        report_content += f"- Models tested: {', '.join(self.models)}\n"
        report_content += f"- Number of questions: {self.num_questions}\n"
        report_content += f"- Results file: {self.results_file}\n\n"
        
        report_content += "## Model Pair Distances\n\n"
        report_content += "Average Euclidean distances between model mean embeddings across all questions:\n\n"
        report_content += avg_distances.to_markdown(index=False, floatfmt=".4f") + "\n\n"
        
        report_content += "## Consistency Metrics\n\n"
        report_content += "### Mean Standard Deviation\n\n"
        report_content += "Average of standard deviations across all embedding dimensions:\n\n"
        report_content += metrics_df.groupby("model")["mean_stddev"].mean().to_markdown(floatfmt=".4f") + "\n\n"
        
        report_content += "### Root-Mean-Square Scatter\n\n"
        report_content += "Root-mean-square of standard deviations across all embedding dimensions:\n\n"
        report_content += metrics_df.groupby("model")["rms_scatter"].mean().to_markdown(floatfmt=".4f") + "\n\n"
        
        report_content += "## Visualizations\n\n"
        report_content += "### Distance Matrix\n\n"
        report_content += "![Distance Matrix](distance_matrix.png)\n\n"
        
        report_content += "### Mean Standard Deviation\n\n"
        report_content += "![Mean Standard Deviation](mean_stddev.png)\n\n"
        
        report_content += "### Root-Mean-Square Scatter\n\n"
        report_content += "![RMS Scatter](rms_scatter.png)\n\n"
        
        # Detailed per-question analysis
        report_content += "## Per-Question Analysis\n\n"
        
        for question in self.questions:
            question_distances = distances_df[distances_df["question"] == question]
            question_metrics = metrics_df[metrics_df["question"] == question]
            
            if len(question_distances) > 0:
                report_content += f"### {question}\n\n"
                
                report_content += "#### Model Distances\n\n"
                report_content += question_distances.to_markdown(index=False, floatfmt=".4f") + "\n\n"
                
                report_content += "#### Consistency Metrics\n\n"
                report_content += question_metrics.to_markdown(index=False, floatfmt=".4f") + "\n\n"
        
        # Save report
        report_path = os.path.join(self.output_dir, "analysis_report.md")
        with open(report_path, "w") as f:
            f.write(report_content)
        
        logger.info(f"Generated report at {report_path}")
        
        return report_path

def main():
    """Main function to run the analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze AI model consistency experiment results")
    parser.add_argument("results_file", help="Path to the pickle file containing raw results")
    parser.add_argument("--num-questions", type=int, default=20, help="Number of questions in the experiment")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.results_file):
        print(f"Error: Results file {args.results_file} not found")
        return
    
    analyzer = ExperimentAnalyzer(args.results_file, args.num_questions)
    report_path = analyzer.generate_report()
    
    print(f"\nAnalysis complete!")
    print(f"Report saved to: {report_path}")
    print(f"Visualizations saved to: {analyzer.output_dir}")

if __name__ == "__main__":
    main()