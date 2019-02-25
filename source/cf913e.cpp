#include<algorithm>
#include<iostream>
#include<cstring>
#include<cstdlib>
#include<string>
using namespace std;
inline int read(){
	register int res=0, c;
	while(c=getchar(), c<'0'||c>'9');
	do{
		res=(res<<3)+(res<<1)+(c^48);
	} while(c=getchar(), c>='0'&&c<='9');
	return res;
}
int const X=0xf, Y=0x33, Z=0x55;
string dp[256][3];
bool upd[256];
bool cmp(string const& a, string const& b){
	return a.length()==b.length()?a<b:a.length()<b.length();
}
void update(int t, string s, int o){
	if(cmp(s, dp[t][o])){
		dp[t][o]=s;
		if(!o && cmp(s, dp[t][1]))dp[t][1]=s;
		if(o<2 && cmp(s, dp[t][2]))dp[t][2]=s;
		upd[t]=1;
	}
}
int main(){
	for(int i=0; i<3*256; i++)
		dp[i/3][i%3]="Rafaaaaaaaaaaaaaaaaaaaaaaaaaaam";
	dp[X][0]=dp[X][1]=dp[X][2]="x", upd[X]=1;
	dp[Y][0]=dp[Y][1]=dp[Y][2]="y", upd[Y]=1;
	dp[Z][0]=dp[Z][1]=dp[Z][2]="z", upd[Z]=1;
	for(int rec=0; rec<10; rec++)
		for(int i=0; i<256; i++)if(upd[i]){
			update(~i&255, '!'+dp[i][0], 0);
			update(~i&255, "!("+dp[i][2]+')', 0);
			for(int j=0; j<3; j++){
				string t=dp[i][j];
				if(j==2)t='('+t+')';
				for(int k=0; k<256; k++){
					update(i&k, t+'&'+dp[k][1], 1);
					update(i&k, t+"&("+dp[k][2]+')', 1);
					update(i&k, dp[k][1]+'&'+t, 1);
					update(i&k, '('+dp[k][2]+")&"+t, 1);
				}
			}
			for(int j=0; j<3; j++){
				string t=dp[i][j];
				for(int k=0; k<256; k++){
					update(i|k, t+'|'+dp[k][2], 2);
					update(i|k, dp[k][2]+'|'+t, 2);
				}
			}
			upd[i]=0;
		}
	int N=read();
	for(int i=1; i<=N; i++){
		int t=0;
		for(int j=7; j>=0; j--)t+=(getchar()-'0')<<j;
		puts(dp[t][2].c_str());
		getchar();
	}
	return 0;
}