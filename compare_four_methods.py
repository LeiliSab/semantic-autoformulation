

import json
import pandas as pd
from pathlib import Path


def load_all_results_jsonl(results_dir, problem_id):
    """Load all results from all_results.jsonl file."""
    results_file = Path(results_dir) / f"problem_{problem_id}" / "all_results.jsonl"
    
    results = []
    if results_file.exists():
        with open(results_file, "r") as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))
    return results


def check_correct(objective_str, gt_value, tolerance=0.0):
    """Check if objective is within tolerance of ground truth."""
    if objective_str is None or gt_value is None:
        return False
    try:
        obj_value = float(objective_str)
        gt_float = float(gt_value)
        if gt_float == 0:
            return abs(obj_value) < tolerance
        else:
            return abs(obj_value - gt_float) / abs(gt_float) <= tolerance
    except:
        return False


def evaluate_method(results, ground_truth, tolerance=0.05):
   
    correct = sum(1 for r in results if check_correct(r.get("best_objective"), ground_truth, tolerance))
    total = len(results)
    accuracy = correct / total if total > 0 else 0.0
    
    return {
        "correct": correct,
        "total": total,
        "accuracy": accuracy
    }


def compare_three_methods(problem_ids=None, start=None, end=None):
    """
    Compare baseline, baseline+exploring_uncertainties, SAC, and SAC+exploring_uncertainties across multiple problems.
    """
    # Load ground truth
    try:
        gt_df = pd.read_json("data/NL4OPT.json", lines=True)
        ground_truth = {i: str(row["en_answer"]) for i, row in gt_df.iterrows()}
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return
    
    # Determine which problems to compare
    if problem_ids is None:
        if start is not None and end is not None:
            problem_ids = list(range(start, end))
        else:
            problem_ids = list(range(len(gt_df)))
    
    # Results storage
    results_summary = []
    
    print("\n" + "="*130)
    print("COMPARING FOUR METHODS - NL4OPT Problems")
    print("="*130 + "\n")
    print(f"{'Problem':<10} {'Baseline':<20} {'Exploring Uncert.':<20} {'SAC':<20} {'SAC+Exp.Uncert.':<20} {'Best':<12}")
    print(f"{'ID':<10} {'Correct/Total (Acc%)':<20} {'Correct/Total (Acc%)':<20} {'Correct/Total (Acc%)':<20} {'Correct/Total (Acc%)':<20}")
    print("-"*130)
    
    total_baseline_correct = 0
    total_baseline_total = 0
    total_uct_correct = 0
    total_uct_total = 0
    total_sac_correct = 0
    total_sac_total = 0
    total_sacuct_correct = 0
    total_sacuct_total = 0
    
    for problem_id in problem_ids:
        if problem_id >= len(gt_df):
            continue
        
        baseline_results = load_all_results_jsonl("NL4OPT_results", problem_id)
        uct_results = load_all_results_jsonl("NL4OPT_results_exploring_uncertainties", problem_id)
        sac_results = load_all_results_jsonl("NL4OPT_results_SAC", problem_id)
        sacuct_results = load_all_results_jsonl("NL4OPT_results_SAC_exploring_uncertainties", problem_id)
        
        if not baseline_results and not uct_results and not sac_results and not sacuct_results:
            continue
        
        gt = ground_truth.get(problem_id, "N/A")
        
        baseline_metrics = evaluate_method(baseline_results, gt, tolerance=0.05)
        uct_metrics = evaluate_method(uct_results, gt, tolerance=0.05)
        sac_metrics = evaluate_method(sac_results, gt, tolerance=0.05)
        sacuct_metrics = evaluate_method(sacuct_results, gt, tolerance=0.05)
        
        baseline_acc = baseline_metrics["accuracy"]
        uct_acc = uct_metrics["accuracy"]
        sac_acc = sac_metrics["accuracy"]
        sacuct_acc = sacuct_metrics["accuracy"]
        
        # Determine best method
        best_acc = max(baseline_acc, uct_acc, sac_acc, sacuct_acc)
        if best_acc == baseline_acc:
            best_method = "Baseline"
        elif best_acc == uct_acc:
            best_method = "UCT"
        elif best_acc == sac_acc:
            best_method = "SAC"
        else:
            best_method = "SAC+UCT"
        
        baseline_str = f"{baseline_metrics['correct']}/{baseline_metrics['total']} ({baseline_acc:.1%})"
        uct_str = f"{uct_metrics['correct']}/{uct_metrics['total']} ({uct_acc:.1%})"
        sac_str = f"{sac_metrics['correct']}/{sac_metrics['total']} ({sac_acc:.1%})"
        sacuct_str = f"{sacuct_metrics['correct']}/{sacuct_metrics['total']} ({sacuct_acc:.1%})"
        
        print(f"{problem_id:<10} {baseline_str:<20} {uct_str:<20} {sac_str:<20} {sacuct_str:<20} {best_method:<12}")
        
        results_summary.append({
            "problem_id": problem_id,
            "baseline_correct": baseline_metrics["correct"],
            "baseline_total": baseline_metrics["total"],
            "baseline_accuracy": baseline_acc,
            "uct_correct": uct_metrics["correct"],
            "uct_total": uct_metrics["total"],
            "uct_accuracy": uct_acc,
            "sac_correct": sac_metrics["correct"],
            "sac_total": sac_metrics["total"],
            "sac_accuracy": sac_acc,
            "sacuct_correct": sacuct_metrics["correct"],
            "sacuct_total": sacuct_metrics["total"],
            "sacuct_accuracy": sacuct_acc,
            "best_method": best_method
        })
        
        total_baseline_correct += baseline_metrics["correct"]
        total_baseline_total += baseline_metrics["total"]
        total_uct_correct += uct_metrics["correct"]
        total_uct_total += uct_metrics["total"]
        total_sac_correct += sac_metrics["correct"]
        total_sac_total += sac_metrics["total"]
        total_sacuct_correct += sacuct_metrics["correct"]
        total_sacuct_total += sacuct_metrics["total"]
    
    # Print totals
    baseline_total_acc = total_baseline_correct / total_baseline_total if total_baseline_total > 0 else 0
    uct_total_acc = total_uct_correct / total_uct_total if total_uct_total > 0 else 0
    sac_total_acc = total_sac_correct / total_sac_total if total_sac_total > 0 else 0
    sacuct_total_acc = total_sacuct_correct / total_sacuct_total if total_sacuct_total > 0 else 0

    baseline_total_str = f"{total_baseline_correct}/{total_baseline_total} ({baseline_total_acc:.1%})"
    uct_total_str = f"{total_uct_correct}/{total_uct_total} ({uct_total_acc:.1%})"
    sac_total_str = f"{total_sac_correct}/{total_sac_total} ({sac_total_acc:.1%})"
    sacuct_total_str = f"{total_sacuct_correct}/{total_sacuct_total} ({sacuct_total_acc:.1%})"

    print("-"*130)
    print(f"{'TOTAL':<10} {baseline_total_str:<20} {uct_total_str:<20} {sac_total_str:<20} {sacuct_total_str:<20}")
    print("="*130 + "\n")
    
    # Count winners
    baseline_wins = sum(1 for r in results_summary if r["best_method"] == "Baseline")
    uct_wins = sum(1 for r in results_summary if r["best_method"] == "UCT")
    sac_wins = sum(1 for r in results_summary if r["best_method"] == "SAC")
    sacuct_wins = sum(1 for r in results_summary if r["best_method"] == "SAC+UCT")
    
    print("\nMETHOD WINS:")
    print(f"  Baseline:  {baseline_wins} problems")
    print(f"  UCT:       {uct_wins} problems")
    print(f"  SAC:       {sac_wins} problems")
    print(f"  SAC+UCT:   {sacuct_wins} problems")
    print()
    
    # Save summary to JSON
    with open("comparison_three_methods.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    print("Summary saved to comparison_three_methods.json\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage:")
            print("  python compare_three_methods.py                # Compare all problems")
            print("  python compare_three_methods.py --range 25 35  # Compare problems 25-34")
            sys.exit(0)
        elif sys.argv[1] == "--range" and len(sys.argv) > 3:
            start = int(sys.argv[2])
            end = int(sys.argv[3])
            compare_three_methods(start=start, end=end)
        else:
            problem_ids = [int(x) for x in sys.argv[1].split(",")]
            compare_three_methods(problem_ids=problem_ids)
    else:
        # Default: compare problems 25-34
        compare_three_methods(start=25, end=35)
