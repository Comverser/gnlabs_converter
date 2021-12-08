my_list = [1,2,56,21,2,4]

sorted_list = sorted(my_list)

print(my_list)
print(sorted_list)

if my_list != sorted_list:
    print('something!')

my_list.sort()

if my_list != sorted_list:
    print('something!2')

print(my_list)
print(sorted_list)