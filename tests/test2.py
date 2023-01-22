from copy import deepcopy
from typing import List, Any


class Matrix:
    def __init__(self, mat: List[Any], shape=None) -> None:
        self.mat = mat
        self.shape = shape

    @staticmethod
    def take_input(row_num, col_num) -> Any:
        ctemp = []
        order = row_num, col_num
        for row in range(order[0]):
            tmp = []
            for col in range(order[1]):
                tmp.append(eval(input("Enter Data:")))
            ctemp.append(tmp)

        return Matrix(ctemp, order)

    def __getitem__(self, item):
        t = self.mat
        for i in item:

            t = t[i]

        return deepcopy(t)

    def __str__(self):
        return f"Matrix({self.shape})"

    def get_row(self, row_no):
        return Matrix(self.mat[row_no])

    def get_column(self, col_no):
        raise NotImplementedError()

    def __mul__(self, other):
        # For now only works for order 2, 2
        if len(self.mat[0]) != len(other):
            raise TypeError("Inconsistent Shapes")

        for i in range(len(self.mat)):
            s = range(len(other[0]))





    def display(self):
        for row in self.mat:
            print(*row)


m = Matrix.take_input(3, 3)
m.display()
print(m[0, 1])

