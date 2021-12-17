test = [1, 1.1, "dd"]

result = [f"{x:.2f}" if type(x) is float else str(x) for x in test]

print(result)
