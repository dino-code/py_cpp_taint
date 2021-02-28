import functions

vals = taint([1.0, 2.0, 3.0, 4.0])

functions.compute_mean(vals)
