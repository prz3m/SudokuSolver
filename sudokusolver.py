# -*- coding: utf-8 -*-
"""
@author: prz3m
"""
import numpy as np


class Sudoku:
    """sudoku board + methods to solve it
    """
    def __init__(self, sudoku_array):
        """
        :param sudoku_array: sudoku borad as a numpy 9x9 array with zeros
                             instead of blanks
        """
        self.sudoku = np.copy(sudoku_array)
        self.init_candidates()
        self.update_candidates()

    def init_candidates(self):
        """initialization of sets of candidates in rows, columns and 3x3 squares
        and sets of candidates for every field in the sudoku board
        """
        self.rows_candidates = []
        self.cols_candidates = []
        self.sq_candidates = []
        for i in range(9):  # don't do sth like 9 * [set()]
            self.rows_candidates.append(set(range(1, 10)))
            self.cols_candidates.append(set(range(1, 10)))
            self.sq_candidates.append(set(range(1, 10)))
        self.sudoku_candidates = np.empty((9, 9), dtype=set)

    def update_candidates(self):
        self.update_row_col_sq_candidates()
        self.update_sudoku_candidates()

    def update_row_col_sq_candidates(self):
        """delete numbers that are already in sudoku from candidates sets
        """
        for i in range(9):
            row_set = set(self.sudoku[i, :])
            self.rows_candidates[i] -= row_set

            col_set = set(self.sudoku[:, i])
            self.cols_candidates[i] -= col_set

            sq_set = set(self.sudoku[3*(i//3):3*(i//3)+3,
                                     3*(i % 3):3*(i % 3)+3].reshape(9))
            self.sq_candidates[i] -= sq_set

    def update_sudoku_candidates(self):
        """find candidates for every field in the sudoku board as an
        intersection of candidates in a row, a column and a 3x3 square
        """
        for i in range(9):
            for j in range(9):
                if self.sudoku[i, j] == 0:
                    self.sudoku_candidates[i][j] = \
                            self.rows_candidates[i]\
                            .intersection(self.cols_candidates[j])\
                            .intersection(
                                self.sq_candidates[(i // 3)*3 + (j // 3)])
                else:
                    self.sudoku_candidates[i, j] = set()

    def put_candidates_in_sudoku(self):
        """updates sudoku item if there is only one candidate
        :returns: counter of changes made to sudoku array
        """
        counter = 0
        for i in range(9):
            for j in range(9):
                if self.sudoku[i, j] == 0 and \
                        len(self.sudoku_candidates[i, j]) == 1:
                    self.sudoku[i, j], = self.sudoku_candidates[i, j]
                    counter += 1
        return counter

    def check_if_solved(self):
        """solved = there are only field with 0 candidates, it doesn't mean that
        the solution is correct!
        """
        return not np.any(self.sudoku == 0)

    def validate(self):
        """validation of solution by checking if there are duplicates in rows,
        columns and 3x3 squares
        """
        for i in range(9):
            row_set_len = len(set(self.sudoku[i, :]))
            col_set_len = len(set(self.sudoku[:, i]))
            sq_set_len = len(set(self.sudoku[3*(i//3):3*(i//3)+3,
                                      3*(i % 3):3*(i % 3)+3].reshape(9)))
            if not (row_set_len == 9 and col_set_len == 9 and sq_set_len == 9):
                return False
        return True

    def solve(self):
        """solving sudoku using elimination
        :returns: true if found solution is correct
        """
        counter = 1
        while counter > 0:
            counter = 0
            counter += self.do_simple_elimination()
            counter += self.do_elimination_in_sudoku(self.eliminate_in_cols)
            counter += self.do_elimination_in_sudoku(self.eliminate_in_rows)
            counter += self.do_elimination_in_sudoku(self.eliminate_in_squares)
        if self.check_if_solved():
            if self.validate():
                return True
        return False

    def do_simple_elimination(self):
        counter = 0
        while True:
            c = self.put_candidates_in_sudoku()
            self.update_candidates()
            counter += c
            if c == 0:
                return counter

    def do_elimination_in_sudoku(self, method):
        counter = 0
        while True:
            c = self.do_elimination_in_elements(method)
            counter += c
            if c == 0:
                return counter

    def do_elimination_in_elements(self, method):
        counter = 0
        for i in range(9):
            for j in range(9):
                candidates = method(i, j)
                intersection = candidates.intersection(
                                                self.sudoku_candidates[i, j])
                if len(intersection) == 1:
                    counter += 1
                    self.sudoku[i, j], = intersection

        self.update_candidates()
        return counter

    def eliminate_in_squares(self, i, j):
        candidates = set(self.sq_candidates[(i // 3)*3 + (j // 3)])
        for k in range((i // 3)*3, (i // 3)*3 + 3):
            for m in range((j // 3)*3, (j // 3)*3 + 3):
                if not (k == i and m == j):
                    candidates -= self.sudoku_candidates[k, m]
        return candidates

    def eliminate_in_cols(self, i, j):
        candidates = set(self.cols_candidates[j])
        m = j
        for k in range(9):
            if not (k == i and m == j):
                candidates -= self.sudoku_candidates[k, m]
        return candidates

    def eliminate_in_rows(self, i, j):
        candidates = set(self.rows_candidates[j])
        k = i
        for m in range(9):
            if not (k == i and m == j):
                candidates -= self.sudoku_candidates[k, m]
        return candidates

    def find_candidates(self, length):
        """returns list of indexes of fields in which there are :param length:
        candidates
        """
        candidates = []
        for i in range(9):
            for j in range(9):
                if len(self.sudoku_candidates[i, j]) == length:
                    candidates.append((i, j))
        return candidates

    def __str__(self):
        sudoku_string = ""
        for i in range(9):
            if i % 3 == 0:
                sudoku_string += "+---+---+---+\n"
            for j in range(9):
                if j % 3 == 0:
                    sudoku_string += "|"
                sudoku_string += str(self.sudoku[i, j])
            sudoku_string += "|\n"
        sudoku_string += "+---+---+---+\n"
        return sudoku_string


class SudokuSolver:
    """load sudoku from CSV file and solve using elimination and, if not
    succesfull, a single guess
    """
    def __init__(self, filepath):
        """
        :param filepath: path of file with sudoku in CSV format, with zeros
        instead of blanks
        """
        self.sudoku_array = np.loadtxt(filepath, delimiter=',', dtype=int)
        if np.any(self.sudoku_array > 9) or np.any(self.sudoku_array < 0):
            raise ValueError("invalid sudoku")
        self.sudoku = Sudoku(self.sudoku_array)

    def solve(self):
        """tries to solve sudoku using elimination
        if it fails, it tries to guess one number and then try again
        usually finds solution quite fast
        it doesn't use bruteforce/backtracking, so it will not handle
        the hardest sudokus
        """

        solved = self.sudoku.solve()
        if solved:
            print("solved without guessing")
        else:
            print("not solved, trying guessing...")
            # try 1 split
            for k in range(2, 10):
                for i, j in self.sudoku.find_candidates(k):
                    for cand in self.sudoku.sudoku_candidates[i, j]:
                        print("i: {0}, j: {1}, cand: {2}".format(i, j, cand))

                        self.sudoku2 = Sudoku(self.sudoku_array)
                        self.sudoku2.sudoku[i, j] = cand
                        self.sudoku2.update_candidates()
                        solved2 = self.sudoku2.solve()
                        if solved2:
                            print("solved with guessing")
                            self.sudoku = self.sudoku2
                            return
                        else:
                            print("not solved")


ss = SudokuSolver("sudoku_trudne272.csv")
ss.solve()
print(ss.sudoku)
