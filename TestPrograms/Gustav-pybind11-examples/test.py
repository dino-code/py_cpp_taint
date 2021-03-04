import functions

vals = [1.0, 2.0, 3.0, 4.0]

vals = taint(vals)

ans1 = functions.compute_mean(vals)

print(ans1)
