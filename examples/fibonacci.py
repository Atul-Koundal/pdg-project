# Example 4 - Fibonacci (the "tricky" loop case)
# Demonstrates: pure loop-carried data dependence.
#
# Across iterations, `a` and `b` each read the value the OTHER held in the
# previous iteration, and `next_val` chains them. This is the loop-carried
# dependence discussed in Section 3.2.1 of the paper, and it is deliberately
# included so the CFG-vs-PDG comparison has a non-trivial case where naive
# reordering would be unsafe.
#
# Slice target: `a` at the final print -> the whole loop is relevant;
# nothing can be eliminated.

n = int(input())
a = 0
b = 1
i = 0
while i < n:
    next_val = a + b
    a = b
    b = next_val
    i = i + 1
print(a)