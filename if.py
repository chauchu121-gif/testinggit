tom,ban = map(int,input().split())
if tom == 1 and ban ==1:
    print ("tomronban")
elif tom==0 and ban ==0:
    print("tom ron sach")
elif tom ==1 and ban !=0:
    print("tomiadun")
else:
    print("tomkhoiadun")