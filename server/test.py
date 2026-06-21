import math
x = [72, 68, 75, 80, 65, 70, 77, 82, 69, 74 ,71, 66, 85, 90, 62, 73, 76, 78, 81, 79, 75, 72, 68, 64, 70, 83, 75, 71, 69, 74]
mean = sum(x) / len(x)
freq = {}
n = len(x)
for number in x: 
    if number in freq:
        freq[number] += 1
    else:
        freq[number] = 1
print(freq)
x_sort = sorted(x)
print(x_sort)
median = 0
if len(x) % 2 == 0: 
    median = (x_sort[len(x) // 2] + x_sort[len(x) // 2 - 1] )/ 2
else: 
    median = x_sort[len(x) // 2]
print(mean)
print(median)

variance = (
    sum(num**2 for num in x)
    - (sum(x)**2)/n
) / (n - 1)

std = math.sqrt(variance)
print(std)