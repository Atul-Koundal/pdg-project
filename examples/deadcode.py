# Example 1 - Straight-line code with dead code
# Demonstrates: dead-code elimination and basic backward slicing.
#
# Slice target: variable `e` at the final print.
#   Expected slice  = {a, b, c, e}
#   Dead code (DCE) = {d}  (d is computed but never affects any output)

a = int(input())
b = int(input())
c = a + b
d = a * 2          # dead: never used by any output
e = c + 1
print(e)