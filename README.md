# Results Data

I could not include result files due to their size and deep folder structures. 

## Generating Results

To reproduce the results, run the batch scripts:

```bash
# Baseline results
python run_NL4OPT.py --index <problem_number>

# Baseline + Exploring Uncertainties
python run_baseline_uct_batch.py "21,24,25,26,27,28,29,30,31,32,33,34"

# SAC results
python run_NL4OPT.py --index <problem_number> --use-sac

# SAC + Exploring Uncertainties
python run_sac_uct_batch.py "21,24,25,26,27,28,29,30,31,32,33,34"
```

Results will be saved to:
- `NL4OPT_results/` - Baseline
- `NL4OPT_results_exploring_uncertainties/` - Baseline + Exploring Uncertainties
- `NL4OPT_results_SAC/` - SAC
- `NL4OPT_results_SAC_exploring_uncertainties/` - SAC + Exploring Uncertainties

## Key Result Files

Each problem folder contains:
- `all_results.jsonl` - All formulation results and metrics
- `all_results_path.json` - Tree structure of explored formulations
- Individual formulation folders with code and evaluations
