#!/bin/bash
# Run all rule-based examples sequentially and report results

PROJ="/Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation"
cd "$PROJ"

declare -A RUNNERS=(
    ["LiquidityDryup"]="examples/LiquidityDryup/run_liquidity.py -c configs/LiquidityDryup/simulation.yml"
    ["MarketCrash"]="examples/MarketCrash/run_crash.py -c configs/MarketCrash/simulation.yml"
    ["ReversalEffect"]="examples/ReversalEffect/run_reversal.py -c configs/ReversalEffect/simulation.yml"
    ["ShortSqueeze"]="examples/ShortSqueeze/run_short_squeeze.py -c configs/ShortSqueeze/simulation.yml"
    ["VolatilityClustering"]="examples/VolatilityClustering/run_volatility.py -c configs/VolatilityClustering/simulation.yml"
)

PASS=0
FAIL=0

for NAME in LiquidityDryup MarketCrash ReversalEffect ShortSqueeze VolatilityClustering; do
    CMD="${RUNNERS[$NAME]}"
    echo "=============================="
    echo "Running: $NAME"
    echo "CMD: python $CMD"
    echo "Start: $(date)"
    
    conda run -n LMSim python $CMD > /tmp/${NAME}_out.txt 2>&1
    EXIT=$?
    
    echo "End: $(date), EXIT=$EXIT"
    
    if [ $EXIT -eq 0 ]; then
        echo "RESULT: PASS ✓"
        PASS=$((PASS+1))
    else
        echo "RESULT: FAIL ✗"
        echo "--- Last 20 lines of output ---"
        tail -20 /tmp/${NAME}_out.txt
        FAIL=$((FAIL+1))
    fi
    echo ""
done

echo "=============================="
echo "Summary: $PASS PASSED, $FAIL FAILED"
echo "=============================="
