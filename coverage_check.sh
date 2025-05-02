#!/usr/bin/env bash
set -euo pipefail

minimum_coverage=80
fail=0

echo "🔍 Required minimum coverage: ${minimum_coverage}%"
echo ""

for pyver in 310 311; do
    covfile=".coverage.py$pyver"
    if [[ -f "$covfile" ]]; then
        echo "🔢 Python 3.$pyver coverage:"
        COVERAGE_FILE=$covfile coverage report --show-missing
        pct=$(COVERAGE_FILE=$covfile coverage report | tail -1 | awk '{print $4}' | tr -d '%')
        echo "📊 Python 3.$pyver: ${pct}%"
        if (( $(echo "$pct < $minimum_coverage" | bc -l) )); then
            echo "❌ Python 3.$pyver coverage is below ${minimum_coverage}%"
            fail=1
        fi
    else
        echo "⚠️ No coverage file found for Python 3.$pyver"
        fail=1
    fi
    echo ""
done

echo "🧪 Combining coverage..."
coverage combine .coverage.py310 .coverage.py311

echo ""
echo "Final Combined Coverage Report (Required: ${minimum_coverage}%)"
if ! coverage report --fail-under=$minimum_coverage --show-missing; then
    echo "❌ Combined coverage is below ${minimum_coverage}%"
    fail=1
fi

coverage erase
exit $fail
