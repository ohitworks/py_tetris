from Core.core import *

l = Line(4)
print("l:", l)
print("DO) l | 0b1010:", l | 0b1010)
print("DO) l ^ 0b0010:", l ^ 0b10)

print("\n-- - + - --\n")

I = Item([2, 2, 3, 1], 0, 1)
print("I:", I)
print("DO) I cut row 0:   ", I.cut_row(0))
print("DO) I cut column 0:", I.cut_column(0))
print("DO) I rotate  90° counterclockwise:", I.rotate_90d_counterclockwise())
print("DO) I rotate 180° counterclockwise:", I.rotate_90d_counterclockwise().rotate_90d_counterclockwise())
print("DO) I rotate 270° counterclockwise:", I.rotate_90d_counterclockwise().rotate_90d_counterclockwise().rotate_90d_counterclockwise())
print("DO) I rotate 360° counterclockwise:", I.rotate_90d_counterclockwise().rotate_90d_counterclockwise().rotate_90d_counterclockwise().rotate_90d_counterclockwise())