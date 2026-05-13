set1 = {1,2,3,4,5}
set2 ={4,5,6,7}
set3 =set1.intersection(set2)
print("set3 value =  ",set3)
set4 = set1.difference(set2)
print("set 4 value =  ", set4)
set5 = set1.union(set2)
print("set 5 value =  ", set5)
set6 = set1.symmetric_difference(set2)
print("set 6 value =  ", set6)
import json
student = {"name":"bobe",
           "age":[1,2,3,4],
           }
student.update( gender ="male", id ="sv01")
tup = student.popitem()
keys = list(student)
print(keys)
print(tup)
print(json.dumps(student, indent= 3))
value = student["name"]
value2= student.get("age")
print(value)
print(value2)
items = list(student.items())
print(items)
