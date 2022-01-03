#include<cstdio>
#include<cstdlib>
#include<cstring>
#include<algorithm>
using namespace std;
int edge[510][510], vis[510], con, N, M, f, t;
void dfs(int x){
	vis[x]=1;
	for(int i=1; i<=N; i++)if(edge[x][i]){
		if(!vis[i])dfs(i);
		else if(vis[i]==1)con++;
		if(con>=2)break;
	}
	vis[x]=2;
}
int main(){
	scanf("%d%d",&N,&M);
	for(int i=1; i<=M; i++){
	    scanf("%d%d",&f,&t);
		edge[f][t]=1;
	}
	for(int i=1; i<=N; i++){
		con=0;
		memset(vis, 0, sizeof vis);
		dfs(i);
		for(int j=1; j<=N; j++)if(j!=i){
			if(!vis[j])dfs(j);
			if(con>=2)break;
		}
		if(con<=1)return puts("YES"), 0;
	}
	return puts("NO"), 0;
}