d = {'a':1,
     'b':2,
     'c':3

     }
new_d ={
    k.upper(): v*2
    for k,v in d.items()

}
print(new_d)