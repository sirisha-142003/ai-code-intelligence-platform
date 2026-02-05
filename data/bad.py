a=[0,1]
n=10
i=2
while i<n:
 b=a[i-1]+a[i-2]
 a.append(b)
 i+=1
print(a)
