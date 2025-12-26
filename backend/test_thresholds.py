"""
Test multiple thresholds to find optimal value for Grade 1 detection
"""
import subprocess
import re
import sys

thresholds = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
num_runs = 3

print("=" * 80)
print("TESTING MULTIPLE THRESHOLDS")
print("=" * 80)
print(f"Running {num_runs} evaluation runs per threshold...\n")

results = []

for threshold in thresholds:
    print(f"\n{'='*80}")
    print(f"Testing threshold: {threshold}")
    print('='*80)

    # Run evaluation
    cmd = [
        sys.executable,  # Use same Python interpreter
        'evaluate_ensemble.py',
        '--runs', str(num_runs),
        '--threshold', str(threshold)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        output = result.stdout

        # Extract overall and Grade 1 accuracy
        overall_match = re.search(r'Overall Accuracy: ([\d.]+)%', output)
        grade1_match = re.search(r'Grade 1: (\d+)/(\d+) = ([\d.]+)%', output)
        grade0_match = re.search(r'Grade 0: (\d+)/(\d+) = ([\d.]+)%', output)

        overall_acc = float(overall_match.group(1)) if overall_match else 0
        grade1_acc = float(grade1_match.group(3)) if grade1_match else 0
        grade0_acc = float(grade0_match.group(1)) if grade0_match else 0

        results.append({
            'threshold': threshold,
            'overall': overall_acc,
            'grade1': grade1_acc,
            'grade0': grade0_acc
        })

        print(f"\nResults for threshold {threshold}:")
        print(f"  Overall: {overall_acc:.1f}%")
        print(f"  Grade 0: {grade0_acc:.1f}%")
        print(f"  Grade 1: {grade1_acc:.1f}%")

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT - skipping threshold {threshold}")
        continue
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

# Summary table
print(f"\n\n{'='*80}")
print("SUMMARY - ALL THRESHOLDS")
print('='*80)
print(f"{'Threshold':<12} {'Overall':<12} {'Grade 0':<12} {'Grade 1':<12}")
print('-' * 80)

for r in results:
    print(f"{r['threshold']:<12.2f} {r['overall']:<12.1f} {r['grade0']:<12.1f} {r['grade1']:<12.1f}")

# Find best threshold
if results:
    best_overall = max(results, key=lambda x: x['overall'])
    best_grade1 = max(results, key=lambda x: x['grade1'])

    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print('='*80)
    print(f"\nBest Overall Accuracy: threshold = {best_overall['threshold']} ({best_overall['overall']:.1f}%)")
    print(f"Best Grade 1 Accuracy: threshold = {best_grade1['threshold']} ({best_grade1['grade1']:.1f}%)")

    # Balanced recommendation
    print(f"\nBalanced Recommendation:")
    print(f"  For medical safety (prioritize Grade 1 detection):")
    print(f"    Use threshold = {best_grade1['threshold']}")
    print(f"    Grade 1: {best_grade1['grade1']:.1f}%, Overall: {best_grade1['overall']:.1f}%")

    print(f"\n  For highest overall accuracy:")
    print(f"    Use threshold = {best_overall['threshold']}")
    print(f"    Overall: {best_overall['overall']:.1f}%, Grade 1: {best_overall['grade1']:.1f}%")

print(f"\n{'='*80}")
print("Update backend/app.py line 116 with chosen threshold")
print('='*80)
