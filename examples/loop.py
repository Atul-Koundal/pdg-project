# Example 3 - While loop
# Demonstrates, in a single loop body:
#   - a loop-INDEPENDENT data dependence:  doubled -> result (same iteration)
#   - a loop-CARRIED data dependence:      result -> result, i -> i (across iterations)
#   - dead code inside a loop:             `unused` is never read
#   - control dependence:                  the loop body is control dependent
#                                          on the predicate `i < n`
#
# Slice target: `result` at the final print.
#   Expected slice excludes `unused`.

n = int(input())
i = 0
result = 0
while i < n:
    doubled = i * 2              # loop-independent: consumed in same iteration
    result = result + doubled    # loop-carried through `result`
    unused = i + 99             # dead code: never used
    i = i + 1
print(result)