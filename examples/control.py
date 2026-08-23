# Example 2 - Conditional
# Demonstrates: control dependence.
#
# The predicate is `x > 0`.
#   `y = x * 2`  is control dependent on the True branch of the predicate.
#   `y = -x`     is control dependent on the False branch of the predicate.
# Neither assignment post-dominates the predicate, which is exactly the
# condition in Definition 3 of the paper.

x = int(input())
y = 0
if x > 0:
    y = x * 2
else:
    y = -x
print(y)