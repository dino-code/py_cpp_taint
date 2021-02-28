import numpy

def pythFunc(m1, m2):
    mat1 = numpy.array(m1)
    mat2 = numpy.array(m2)
    #mat4 = []  # for use in Taint Return test 2

    mat3 = numpy.multiply(mat1,mat2)

    mat3 = [list(i) for i in mat3]

    return mat3