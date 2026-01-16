"""
run_sac_exploring_uncertainties_batch.py

Run multiple NL4OPT problems with SAC and exploring uncertainties (uncertainty-augmented search).
"""

from MCTS_used import MCTS
import pandas as pd
import sys


def run_problem_with_sac_exploring_uncertainties(problem_index, gamma=0.1):

    print(f"\n{'='*80}")
    print(f"Running Problem {problem_index} with SAC + Exploring Uncertainties (gamma={gamma})")
    print(f"{'='*80}\n")
    
    # Load problem data
    df = pd.read_json("data/NL4OPT.json", lines=True)
    problem_str = df.iloc[problem_index].en_question
    ground_truth = df.iloc[problem_index].en_answer
    
    # Initialize MCTS with SAC enabled and uncertainty term
    mcts = MCTS(use_sac=True, gamma=gamma)
    
    # Run DFS and save to SAC+exploring_uncertainties results folder
    results_dir = f"NL4OPT_results_SAC_exploring_uncertainties/problem_{problem_index}"
    
    try:
        mcts.dfs_from_scratch(problem_str, results_dir, ground_truth=ground_truth)
        print(f"\n[OK] Problem {problem_index} completed successfully")
        print(f"Results saved to {results_dir}")
        return True
    except Exception as e:
        print(f"\n[FAILED] Problem {problem_index} error: {e}")
        return False


def run_batch(problem_ids, gamma=0.1):
    
    results = {}
    
    print(f"\n{'='*80}")
    print(f"Batch Run: {len(problem_ids)} problems with SAC + Exploring Uncertainties")
    print(f"Problems: {problem_ids}")
    print(f"Gamma: {gamma}")
    print(f"{'='*80}\n")
    
    for i, problem_id in enumerate(problem_ids, 1):
        print(f"\n[{i}/{len(problem_ids)}] Starting problem {problem_id}...")
        success = run_problem_with_sac_exploring_uncertainties(problem_id, gamma=gamma)
        results[problem_id] = "Success" if success else "Failed"
    
    # Print summary
    print(f"\n\n{'='*80}")
    print("BATCH RUN SUMMARY")
    print(f"{'='*80}")
    print(f"{'Problem':<12} {'Status':<20}")
    print("-"*80)
    for problem_id, status in results.items():
        print(f"{problem_id:<12} {status:<20}")
    
    successes = sum(1 for s in results.values() if s == "Success")
    print("-"*80)
    print(f"Total: {successes}/{len(problem_ids)} successful")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Default problem list: 25-34
    default_problems = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
    
    if len(sys.argv) > 1:
        # Custom problem list from command line
        problem_ids = [int(x) for x in sys.argv[1].split(",")]
        gamma = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
    else:
        # Use default list
        problem_ids = default_problems
        gamma = 0.1
    
    run_batch(problem_ids, gamma=gamma)
