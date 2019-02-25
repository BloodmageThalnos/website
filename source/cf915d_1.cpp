#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;
typedef long long ll;

int n, m;
vector<vector<int>> g;
vector<int> used2;

bool flag = false, f = false;   //这两个flag在第一次dfs中用于回溯时记录环。其实用栈来记录会更直观一些。
int u;
vector<pair<int, int>> e;

void dfs1(int v) {
	used2[v] = 1;
	for (int i = 0; i < g[v].size(); i++) {
		int to = g[v][i];
		if (used2[to] == 1) {
			flag = true;
			u = to;
			e.emplace_back(v, to);
				return;
		}
		else {
			if (used2[to] == 0) {
				dfs1(to);
				if (f) {
					return;
				}
				if (flag) {
					e.emplace_back(v, to);
					if (u == v) {
						f = true;
					}
					return;
				}
			}
		}
	}
	used2[v] = 2;
}


bool ans = false, n_f = false;
int x, y;

void dfs2(int v) {
	used2[v] = 1;
	for (int i = 0; i < g[v].size(); i++) {
		int to = g[v][i];
		if (used2[to] == 1 && !(x == v && y == to)) {
			n_f = true;
		}
		if (used2[to] == 0 && !(x == v && y == to)) {
			dfs2(to);
		}
	}
	used2[v] = 2;
}

int main() {
	ios_base::sync_with_stdio(0);
	cin.tie(0);
	cout.tie(0);
	cin >> n >> m;
	g.assign(n + 1, vector<int>());
	for (int i = 0; i < m; i++) {
		int v, u;
		cin >> v >> u;
		g[v].push_back(u);
	}
	used2.assign(n + 1, 0);

	for (int i = 1; i <= n; i++) {
		if (used2[i] == 0) {
			dfs1(i);
		}
	}

	for (int i = 0; i < e.size(); i++) {
		n_f = false;
		used2.assign(n + 1, 0);
		x = e[i].first;
		y = e[i].second;
		for (int i = 1; i <= n; i++) {
			if (!used2[i]) {
				dfs2(i);
			}
		}
		if (!n_f) {
			cout << "YES";
			return 0;
		}
	}
	if (e.size() == 0) {
		cout << "YES";
	}
	else {
		cout << "NO";
	}
}