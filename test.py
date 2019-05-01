test_arr = []

for i in range(5):
    test_arr.append((i,2*i))
print(test_arr)

print(list(map(lambda p: p[0], test_arr)))

result = []

for sum in test_arr:
    result.append(sum[0])

print(result)