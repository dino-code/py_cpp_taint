import final

matOne = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
matTwo = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

matOne, matTwo = taint(matOne, matTwo)

matThree = final.pythFunc(matOne, matTwo)
sink(matThree)
def sink(mat):
	return mat

def taint(x, y):
	return x, y

