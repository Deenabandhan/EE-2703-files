# The function edge_cases() is used to evaluate the possible errors that could happen
def edge_cases(matrix1, matrix2):
    s1 = set()  # This set is to check the number of row elements in matrix1
    s2 = set()  # This set is to check the number of row elements in matrix2

    dat = []  # This list stores the datatype of all elements

    data_type = [
        type(1),
        type(1.0),
        type(1 + 2j),
    ]  # Allowed datatypes of elements in matrix

    # The following statement checks if any one of the given matrices is empty
    if len(matrix1) * len(matrix2) == 0:
        raise ValueError("Array is empty")

    # The following statement checks if the the matrices are iterable and checks the datatype of each element
    try:
        for i in matrix1:
            s1.add(len(i))
            lst = [(type(j) in data_type) for j in i]
            dat.extend(lst)
        for i in matrix2:
            s2.add(len(i))
            lst = [(type(j) in data_type) for j in i]
            dat.extend(lst)
    except TypeError:
        raise ValueError("Array is not two dimensional")

    # The following statement checks if number of elements in each row of the matrix are equal
    if len(s1) != 1 or len(s2) != 1:
        raise ValueError("The number of elements in each row is not equal")

    # The following statement checks if the datatype of any element is different from what we have listed
    if False in dat:
        raise TypeError("The datatype of the element is not right")

    # The following condition checks the rule for matrix multiplication

    if len(matrix2) != len(matrix1[0]):
        raise ValueError("Array dimensions don't match")


def matrix_multiply(matrix1, matrix2):
    edge_cases(matrix1, matrix2)  # The function is called to check the edge cases
    # After running the above function call , we are sure that we can perform multiplication on the given matrices
    m = len(matrix1)
    k = len(matrix1[0])  # This is also equal to len(matrix2)
    n = len(matrix2[0])
    prod = []  # This stores the result of the multiplication and its dimension is m*n
    for i in range(m):
        prod.append([])
        for j in range(n):
            sum = 0
            for u in range(k):
                sum += matrix1[i][u] * matrix2[u][j]  # Multiplication is performed
            prod[i].append(sum)
    return prod
