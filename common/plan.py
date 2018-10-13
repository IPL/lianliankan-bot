#Copyright https://github.com/ZhangFengze/QQLianLianKanCheat

# find first step
def solve_matrix_one_step(matrix):
    matrix_row = len(matrix)
    matrix_col = len(matrix[0])
    for row in range(matrix_row):
        for col in range(matrix_col):
            # can't start from empty
            if matrix[row][col] == 0:
                continue
            target_row,target_col = DFS(row,col,
                                        target_number=matrix[row][col],
                                        empty_number=0,
                                        matrix=matrix,
                                        matrix_row=matrix_row,matrix_col=matrix_col,
                                        path=str(),
                                        first_step=True)
            if target_row:
                return row,col,target_row,target_col

    # solved, or no solution

    for row in range(matrix_row):
        for col in range(matrix_col):
            if matrix[row][col] != 0:
                # no solution
                print("no solution??")
    # all empty, solved
    return None

def in_range(row,col,matrix_row,matrix_col):
    if row < 0\
        or col < 0\
        or row >= matrix_row\
        or col >= matrix_col:
        return False
    return True

def used_lines(path):
    # '0' up
    # '1' right
    # '2' down
    # '3' left
    used_lines = 0
    last_char = 'x' # for start, must be different
    for char in path:
        if char != last_char:
            used_lines+=1
        last_char = char
    return used_lines

# DFS, stop once the path used over 3 lines
def DFS(now_row,now_col,
        target_number,
        empty_number,
        matrix,matrix_row,matrix_col,
        path,
        first_step):

    # first step doesn't check state
    if not first_step:
        # check state

        # check in range
        if not in_range(now_row,now_col,matrix_row,matrix_col):
            return None,None

        # check path used over 3 lines?
        if used_lines(path) > 3:
            return None,None

        # it's graph DFS, but we don't check if we've been here
        # because we can only use at most 3 lines
        # and we don't go back..
        pass

        # check now number
        my_number = matrix[now_row][now_col]
        # found!
        if my_number == target_number:
            return now_row,now_col

        # wrong way..
        # we can only wall on empty
        if my_number != empty_number:
            return None,None

    # check over state
    # now we are on empty grid or start grid

    # go up
    if path == str() or path[-1] != '2':

    # can't go back, if last time we go down...

        new_path = path + '0'
        target_row,target_col = DFS(now_row - 1,now_col,
                                    target_number,
                                    empty_number,
                                    matrix,matrix_row,matrix_col,
                                    new_path,
                                    first_step=False)
        if target_row:
            return target_row,target_col

    # go right
    if path == str() or path[-1] != '3':

    # can't go back, if last time we go left...

        new_path = path + '1'
        target_row,target_col = DFS(now_row,now_col + 1,
                                    target_number,
                                    empty_number,
                                    matrix,matrix_row,matrix_col,
                                    new_path,
                                    first_step=False)
        if target_row:
            return target_row,target_col

    # go down
    if path == str() or path[-1] != '0':

    # can't go back, if last time we go up...

        new_path = path + '2'
        target_row,target_col = DFS(now_row + 1,now_col,
                                    target_number,
                                    empty_number,
                                    matrix,matrix_row,matrix_col,
                                    new_path,
                                    first_step=False)
        if target_row:
            return target_row,target_col

    # go left
    if path == str() or path[-1] != '1':

    # can't go back, if last time we go right...

        new_path = path + '3'
        target_row,target_col = DFS(now_row,now_col - 1,
                                    target_number,
                                    empty_number,
                                    matrix,matrix_row,matrix_col,
                                    new_path,
                                    first_step=False)
        if target_row:
            return target_row,target_col

    # all failed..
    return None,None

def print_matrix(matrix):
    for row in range(len(matrix[0])):
        line = str()
        for col in range(len(matrix)):
            if matrix[col][row] == 0:
                id = '  '
            else:
                id = '%02d' % matrix[col][row]
            line+='%s  ' % id
        print(line)
