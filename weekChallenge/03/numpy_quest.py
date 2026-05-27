# NumPy 미니퀘스트 모음
import numpy as np
from utils.utils import printanswer

# ============================================================
# Quest 1 - Dimension (차원)
# ============================================================
print("\n===== Quest 1 - Dimension (차원) =====")

## 1
array = np.array([[[1,2], [3,4]], [[5,6],[7,8]]])

printanswer(1, str(array.ndim))

## 2
array = np.array([10, 20, 30, 40, 50, 60])
array = array.reshape(2,3)

printanswer(2, str(array.shape))

## 3
array = np.array([7,14,21])
array = array[:, np.newaxis]
answerlist = []
answerlist.append(str(array))
answerlist.append(str(array.shape))

printanswer(3, answerlist)

# ============================================================
# Quest 2 - Shape (형태)
# ============================================================
print("\n===== Quest 2 - Shape (형태) =====")

## 1
array = np.array([[1, 2, 3], [4, 5, 6]])

printanswer(1, array.shape)

## 2
array = np.array([10, 20, 30, 40, 50, 60])
array = array.reshape(2,3)

printanswer(2, array)

## 3
array = np.array([1,2,3,4,5,6,7,8,9,10,11,12])

array = array.reshape(3, 2, 2)

printanswer(3, array)

# ============================================================
# Quest 3 - Data Type (데이터 타입)
# ============================================================
print("\n===== Quest 3 - Data Type (데이터 타입) =====")

## 1
array = np.array([10, 20, 30])

printanswer(1, array.dtype)

## 2
array = np.float64(array)

printanswer(2, array.dtype)

## 3
array = np.array([100,200,300])

array = np.uint8(array)

printanswer(3, array.itemsize)

# ============================================================
# Quest 4 - Indexing (인덱싱)
# ============================================================
print("\n===== Quest 4 - Indexing (인덱싱) =====")

## 1
array = np.array([10, 20, 30, 40, 50])

answerlist = [array[0], array[-1]]
printanswer(1, answerlist)

## 2
array = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

answerlist = []
firstcolumn = array[:, 0]
answerlist.append(f"first column: {firstcolumn}")

secondrow = array[1, :]
answerlist.append(f"second row: {secondrow}")
printanswer(2, answerlist)

## 3
array = np.array([5,15,8,20,3,12])

answerlist = []

answerlist.append([i for i, x in enumerate(array) if x > 10])

printanswer(3, answerlist)

# ============================================================
# Quest 5 - Operations (연산)
# ============================================================
print("\n===== Quest 5 - Operations (연산) =====")

## 1
a = np.array([1,2,3])
b = np.array([4,5,6])

answerlist = a + b
printanswer(1, answerlist)

## 2
matrix = np.array([[10,20,30], [40,50,60]])
vector = np.array([1,2,3])

answerlist = matrix + vector

printanswer(2, answerlist)

## 3
array = np.array([[3,7,2], [8,4,6]])

index = next(i for i, x in np.ndenumerate(array) if x == np.max(array))[0]
printanswer(3, array[index])

# ============================================================
# Quest 6 - Universal Functions (유니버설 함수)
# ============================================================
print("\n===== Quest 6 - Universal Functions (유니버설 함수) =====")

## 1
array = np.array([1, 2, 3, 4])
array = np.multiply(array, array)

printanswer(1, array)

## 2
array1 = np.array([10, 20, 30])
array2 = np.array([1, 2, 3])

array1 = np.add(array1, array2)

printanswer(2, array1)

## 3
array = np.array([1, np.e, 10, 100])
array = np.log10(array)
array = [x for x in array if x > 1]
printanswer(3, array)
