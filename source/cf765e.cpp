#include<stdio.h>
#include<vector>
#include<set>
const int maxn=200020;
std::vector<int>edge[maxn];
int N,q;
int cut(int t){
    while(!(t&1))t>>=1;
    return t;
}
int dfs(int n,int pre){
    int deg=edge[n].size();
    if(deg==1)return 1;
    else if(deg==2)return 1+dfs((pre==edge[n][0])?edge[n][1]:edge[n][0],n);
    else{
        std::set<int>s;
        for(int i=0;i<deg;i++)if(edge[n][i]!=pre)
            s.insert(dfs(edge[n][i],n));
        if(s.size()==1)return *s.begin()+1;
        if(q)printf("-1\n"),exit(0);
        if(pre)q=1,s.insert(dfs(pre,n));
        if(s.size()>=3)printf("-1\n"),exit(0);
        printf("%d\n",cut(*s.begin()+*s.rbegin()));
        exit(0);
    };
}
int main(){
    scanf("%d",&N);
    for(int i=1;i<N;i++){
        scanf("%d%d",&u,&v);
        edge[u].push_back(v); edge[v].push_back(u);
    }
    for(int i=1;i<=N;i++)if(edge[i].size()>2)
        return 0*printf("%d",cut(dfs(i,0)));
    printf("%d",cut(N-1));
    return 0;
}