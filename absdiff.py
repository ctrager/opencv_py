import numpy as np
import cv2
import time


m1 = (
((1,1,1),(1,1,3),(1,1,1)),
((1,1,1),(1,1,1),(1,1,1)),
)

m2 = (
((1,1,1),(1,1,1),(1,1,1)),
((1,1,1),(7,1,1),(1,1,1)),
)

a = np.uint8(m1)
b = np.uint8(m2)


diff = cv2.absdiff(a, b)
suma = np.sum(a)
sumb = np.sum(b)

gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
nonzero = cv2.countNonZero(gray)

print(diff)
print(gray)
print(nonzero)
