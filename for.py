for i in range(0, 5):
    print(i,end ='')
d = {
    "a":1,
    "b":2,
    "c":3,
}
for item in d.items():
    print(item)
for value in d.values():
    for key in d.keys():
        print(key)


                