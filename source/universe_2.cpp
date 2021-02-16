#include <iostream>
#include <fstream>
#include <random>
#include <string>
#include <sstream>
#include <vector>
#include <math.h>
#define NUM_PLANETS 10000
#define INITIAL_SPEED
//#define TIME_PER_ITER 0.016666667 /* 60 fps */
#define TIME_PER_ITER 1
#define MAX_ITER 3600
using std::vector;
const double eps = 1e-9;
const double min_dist = 1;
const double G = 1e-3; /* 万有引力常数 */

class Vector{
public:
	double x, y, z;
	Vector() :x(0), y(0), z(0){}
	Vector(double x1, double y1, double z1) :x(x1), y(y1), z(z1){}
	Vector(const Vector &v) :x(v.x), y(v.y), z(v.z){}
	~Vector(){};
	void operator=(const Vector &v);
	Vector operator+(const Vector &v);
	Vector operator-(const Vector &v);
	Vector operator/(const Vector &v);
	Vector operator*(const Vector &v);
	Vector operator+(double f);
	Vector operator-(double f);
	Vector operator/(double f);
	Vector operator*(double f);
	double dot(const Vector &v);
	double length();
	void normalize();
	Vector crossProduct(const Vector &v);
	friend std::ostream& operator<<(std::ostream& cout, Vector v);
};
void Vector::operator=(const Vector &v)
{
	x = v.x;
	y = v.y;
	z = v.z;
}
Vector Vector::operator+(const Vector &v)
{
	return Vector(x+v.x, y+v.y, z+v.z);
}
Vector Vector::operator-(const Vector &v)
{
	return Vector(x-v.x, y-v.y, z-v.z);
}
Vector Vector::operator/(const Vector &v)
{
	if(fabsf(v.x) <= eps || fabsf(v.y) <= eps || fabsf(v.z) <= eps)
	{
		std::cerr<<"Divide by zero error."<<std::endl;
		return *this;
	}
	return Vector(x/v.x, y/v.y, z/v.z);
}
Vector Vector::operator*(const Vector &v)
{
	return Vector(x*v.x, y*v.y, z*v.z);
}
Vector Vector::operator+(double f)
{
	return Vector(x+f, y+f, z+f);
}
Vector Vector::operator-(double f)
{
	return Vector(x-f, y-f, z-f);
}
Vector Vector::operator/(double f)
{
	if(fabsf(f) < eps)
	{
		std::cerr<<"Divide by zero error."<<std::endl;
		return *this;
	}
	return Vector(x/f, y/f, z/f);
}
Vector Vector::operator*(double f)
{
	return Vector(x*f, y*f, z*f);
}
double Vector::dot(const Vector &v)
{
	return x*v.x + y*v.y + z*v.z;
}
double Vector::length()
{
	return sqrtf(dot(*this));
}
void Vector::normalize()
{
	double len = length();
	if(len < eps) len = 1;
	len = 1/len;

	x *= len;
	y *= len;
	z *= len;
}
Vector Vector::crossProduct(const Vector &v)
{
	return Vector(y * v.z - z * v.y,
		z * v.x - x * v.z,
		x * v.y - y * v.x);
}
std::ostream& operator<<(std::ostream& cout, Vector v)
{
	cout<<v.x<<" "<<v.y<<" "<<v.z<<" ";
	return cout;
}
struct Tree{
	int son[8];
	int bob;
	Vector center;
	double mass;
};

vector<Tree> tree;

struct Planet{
	Vector pos; // 位置
	Vector v;   // 速度
//	Vector a;   // 加速度
	double m;   // 质量
}planet[NUM_PLANETS+1];
bool nome[NUM_PLANETS+1]; // 已经飞出地图的点

void insertNode(int r, int v, double sx, double sy, double sz, double size){
	double mass = 0;
	Vector center = Vector();
	size/=2;
	int cx = planet[v].pos.x < sx+size, cy = planet[v].pos.y < sy+size, cz = planet[v].pos.z < sz+size,
		index = (cx<<2)|(cy<<1)|cz;
	if(!tree[r].son[0]){
		if(tree[r].bob){
			for(int i=0; i<8; i++){
				tree.emplace_back();
				tree[r].son[i] = tree.size()-1;
			}
			int bx = planet[tree[r].bob].pos.x < sx+size, by = planet[tree[r].bob].pos.y < sy+size, bz = planet[tree[r].bob].pos.z < sz+size, inbex = (bx<<2)|(by<<1)|bz;
			insertNode(tree[r].son[inbex], tree[r].bob, sx+bx*size, sy+by*size, sz+by*size, size);
			insertNode(tree[r].son[index], v, sx+cx*size, sy+cy*size, sz+cy*size, size);
			tree[r].bob = NULL;
		}
		else{
			tree[r].bob = v;
			mass = planet[v].m;
			center = planet[v].pos;
		}
	}
	else{
		insertNode(tree[r].son[index], v, sx+cx*size, sy+cy*size, sz+cy*size, size);
	}
	if(!tree[r].son[0]){
		for(int i=0; i<8; i++){
			Tree& n = tree[tree[r].son[i]];
			if(n.mass){
				center = (center*mass + n.center*n.mass)/(mass+n.mass);
				mass += n.mass;
			}
		}
	}
	tree[r].center = center;
	tree[r].mass = mass;
}

int main(){
	int n=NUM_PLANETS;
	std::default_random_engine engine;
	std::uniform_real_distribution<double> unifx(-1000., 1000.);
	std::normal_distribution<double> unify(0., 100.);
	std::uniform_real_distribution<double> unifz(-1000., 1000.);
	std::uniform_real_distribution<double> unifa(0, 2*3.1415926);
#ifdef INITIAL_SPEED
	std::uniform_real_distribution<double> univx(-20./TIME_PER_ITER, 20./TIME_PER_ITER);
	std::uniform_real_distribution<double> univy(-3./TIME_PER_ITER, 3./TIME_PER_ITER);
	std::uniform_real_distribution<double> univz(-20./TIME_PER_ITER, 20./TIME_PER_ITER);
#endif
	std::normal_distribution<double> norm(10000., 5000.);

	for(int i=1; i<=n; i++){
		/*
		planet[i].pos.x = unifx(engine);
		planet[i].pos.z = unifz(engine);
		*/
		double r = unifx(engine);
		double a = unifa(engine);
		planet[i].pos.x = r*sin(a);
		planet[i].pos.z = r*cos(a);
		planet[i].pos.y = unify(engine);
#ifdef INITIAL_SPEED
		/*
		planet[i].v.x = univx(engine);
		planet[i].v.z = univz(engine);
		*/
		double l = univx(engine);
		planet[i].v.x = l*sin(a+3.1415926/2);
		planet[i].v.z = l*cos(a+3.1415926/2);
		planet[i].v.y = univy(engine);
#endif
		planet[i].m = abs(norm(engine)) + 100.; // in case negative if you are so lucky
	}

	planet[0].m = 1200000;
	planet[0].pos= Vector(0, 0, 0);	// a big sun

	std::ofstream fout("init.dat");
	for(int i=1; i<=n; i++){
		fout<<planet[i].pos<<planet[i].v<<planet[i].m<<" ";
	}
	fout.close();

	tree.emplace_back();
	//tree.push_back(Tree());

	for(int it=0; it<MAX_ITER; it++){	// calculate for every iteration
		for(int i=1; i<=n; i++){
			insertNode(0, i, -3200., -3200., -3200., 6400.);
		}

		// change position
		for(int i=1; i<=n; i++)if(!nome[i]){
			planet[i].pos = planet[i].pos + planet[i].v * TIME_PER_ITER;

			if(abs(planet[i].pos.x)>3200. || abs(planet[i].pos.y)>3200. || abs(planet[i].pos.z)>3200.){
				// skip if it flies out of space.
				nome[i] = true;
				planet[i].v = Vector();
			}
		}
		std::cout<<"Time = " << it << ", pos: " << planet[1].pos << std::endl;

		FILE* fout = fopen((std::to_string(it)+".dat").c_str(), "wb");
		for(int i=1; i<=n; i++){
			float f[3] ={planet[i].v.x, planet[i].v.y, planet[i].v.z};
			fwrite(&f, sizeof(float), 3, fout);
		}
		fclose(fout);
	}
	return 0;
}
