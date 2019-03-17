s,tt=input(),input()
times,now,leng,t=0,0,1,tt[:1]
for i in range(1,len(tt)):
    if tt[i]==tt[now]:
        now+=1
        if now==leng:
            now=0
            times+=1
    else:
        t+=tt[:leng]*times+tt[:now]+tt[i]
        leng=i+1
        now=0
        times=0
a,b,c,d=s.count('0'),s.count('1'),t.count('0'),t.count('1')
n=min(a//c if c!=0 else 0,b//d if d!=0 else 0)
ttt=tt[:now]
e,f=ttt.count('0'),ttt.count('1')
if a-c*n>=e and b-d*n>=f:
    print(t*n+ttt+'0'*(a-c*n-e)+'1'*(b-d*n-f))
else:
    print(t*n+'0'*(a-c*n)+'1'*(b-d*n))