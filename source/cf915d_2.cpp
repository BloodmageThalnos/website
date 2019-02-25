#include <bits/stdc++.h>

#define rep(i, j, k) for (int i = j; i < k; i ++)

using namespace std;

const int N = 510;

int n, m, c, e[N][N], d[N], g[N], vis[N];

void dfs(int u) {
    vis[u] = 1, c --;
    rep (i, 1, n + 1)
        if (!vis[i] && e[u][i])
            if ((-- d[i]) <= 0) dfs(i);
}

int main() {
    ios::sync_with_stdio(false);
    cin >> n >> m;
    int u, v;
    rep (i, 0, m) {
        cin >> u >> v;
        e[u][v] = 1, g[v] ++;
    } 
    rep (i, 1, n + 1) {
        rep (j, 1, n + 1)
            d[j] = g[j], vis[j] = 0;
        d[i] --, c = n;
        rep (j, 1, n + 1)
            if (d[j] <= 0 && !vis[j])
                dfs(j);
        if (!c) {
            puts("YES");
            return 0;
        }
    }
    puts("NO");
}