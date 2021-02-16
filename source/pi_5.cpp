#include "mpi.h"
#include <iostream>
#include <fstream>
#include <math.h>
#include <Windows.h>
#include <boost/multiprecision/cpp_bin_float.hpp>
using namespace boost::multiprecision;

#define PRECISION 25000
typedef number<cpp_bin_float<PRECISION> > pi_type;
typedef int a_type;

const int ITER=2400;

pi_type pi, pi_exact;

int main(int argc, char *argv[])
{
	std::ifstream fin("d:\\pi.txt");
	char buf[PRECISION+2];
	fin.get(buf, PRECISION+1);
	pi_exact = pi_type(buf);
	// 从文件读入Pi的精确值，用于计算精度。

	double startwtime = clock(), endwtime;

	long long K=6, L=13591409;
	pi_type M=1, X=1, S=13591409;
	for(int i=1; i<=ITER; i++){
		M = floor((pow(K, 3)-16*K)*M/pow(i,3));
		L += 545140134;
		X *= -262537412640768000.l;
		S += M * L / X;
		K += 12;
		// std::cout<<M<<"  "<<X<<"  "<<S<<std::endl;
	}
	pi = 426880 * sqrt(pi_type(10005)) / S;
	std::cout << std::defaultfloat << std::setprecision(PRECISION);
	std::cout << "pi is approximately " << pi << std::endl;
	std::cout << std::scientific << std::setprecision(5);
	std::cout << "Error is " << boost::multiprecision::fabs(pi - pi_exact) <<  std::endl;
	/*printf("pi is approximately %.16f, Error is %.16f\n", pi, fabs(pi - pi_exact));*/
	endwtime = clock();
	printf("wall clock time = %f s\n", (endwtime-startwtime)/1000.);

	system("pause");
	return 0;
}
