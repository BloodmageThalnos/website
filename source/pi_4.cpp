#include "mpi.h"
#include <iostream>
#include <fstream>
#include <math.h>
#include <boost/multiprecision/cpp_bin_float.hpp>
using namespace boost::multiprecision;

#define PRECISION 10000
typedef number<cpp_bin_float<PRECISION> > pi_type;
typedef int a_type;

double solve(int id){
	double res, series(int, int);
	res = 4.*series(1, id) - 2.*series(4, id) - series(5, id) - series(6, id);
	res = res - floor(res);
	//auto temp = (*((long long*)(&res)))&0xFFFFFFFFFFF00000L;
	//return *(double*)&temp;
	return floor(res*4294967296.l)/4294967296.0;
}

double series(int m, int id)
/*  This routine evaluates the series  sum_k 16^(id-k)/(8*k+m)
	using the modular exponentiation technique. */
{
	int k;
	double ak, eps=1e-17, p, s=0, t, expm(double, double);

	/*  Sum the series up to id. */

	for(k = 0; k < id; k++){
		ak = 8 * k + m;
		p = id - k;
		t = expm(p, ak);
		s = s + t / ak;
		s = s - (int)s;
	}

	/*  Compute a few terms where k >= id. */

	for(k = id; k <= id + 100; k++){
		ak = 8 * k + m;
		t = pow(16., (double)(id - k)) / ak;
		if(t < eps) break;
		s = s + t;
		s = s - (int)s;
	}
	return s;
}

double expm(double p, double ak)
/*  expm = 16^p mod ak.  This routine uses the left-to-right binary
	exponentiation scheme. */
{
	int i, j;
	double p1, pt, r;
#define ntp 25
	static double tp[ntp];
	static int tp1 = 0;

	/*  If this is the first call to expm, fill the power of two table tp. */

	if(tp1 == 0) {
		tp1 = 1;
		tp[0] = 1.;

		for(i = 1; i < ntp; i++) tp[i] = 2. * tp[i-1];
	}

	if(ak == 1.) return 0.;

	/*  Find the greatest power of two less than or equal to p. */

	for(i = 0; i < ntp; i++) if(tp[i] > p) break;

	pt = tp[i-1];
	p1 = p;
	r = 1.;

	/*  Perform binary exponentiation algorithm modulo ak. */

	for(j = 1; j <= i; j++){
		if(p1 >= pt){
			r = 16. * r;
			r = r - (int)(r / ak) * ak;
			p1 = p1 - pt;
		}
		pt *= .5;
		if(pt >= 1.){
			r = r * r;
			r = r - (int)(r / ak) * ak;
		}
	}

	return r;
}

pi_type pi_exact;

int main(int argc, char *argv[])
{
	std::ifstream fin("d:\\pi.txt");
	char buf[PRECISION+2];
	fin.get(buf, PRECISION+1);
	pi_exact = pi_type(buf);
	// 从文件读入Pi的精确值，用于计算精度。

	int myid, numprocs, done = 0, namelen;
	double startwtime = 0.0, endwtime;
	char processor_name[MPI_MAX_PROCESSOR_NAME];

	MPI_Init(&argc, &argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &myid);
	MPI_Get_processor_name(processor_name, &namelen);

	fprintf(stdout,"Process %d of %d is on %s\n",
		myid+1, numprocs, processor_name);
	fflush(stdout);

	while(!done) {
		a_type n, i;
		if(myid == 0) {
			fprintf(stdout, "Enter the number of iterations: (0 quits) ");
			fflush(stdout);
			std::cin >> n;
			n = n*log(10)/log(16);
			startwtime = MPI_Wtime();
		}
		MPI_Bcast(&n, sizeof(n), MPI_BYTE, 0, MPI_COMM_WORLD);
		if(!n) 
			done = 1;
		else {
			pi_type pi=3, sum=0;
			for(i = myid*8; i < n; i += numprocs*8) {
				auto j=pow(pi_type(1/16.), i)*solve(i);
				//std::cout << std::scientific << std::setprecision(30) << j << std::endl;
				sum += j;
			}
			pi_type *in = NULL;
			if(myid == 0) {
				in = (pi_type*)malloc(sizeof(pi_type)*numprocs);
			}
			MPI_Gather(&sum, sizeof(sum), MPI_BYTE, in, sizeof(sum), MPI_BYTE, 0, MPI_COMM_WORLD);

			if(myid == 0) {
				for(int i=0; i<numprocs; i++){
					pi += in[i];
				}
				std::cout << std::defaultfloat << std::setprecision(PRECISION);
				std::cout << "pi is approximately " << pi << std::endl;
				std::cout << std::scientific << std::setprecision(5);
				std::cout << "Error is " << boost::multiprecision::fabs(pi - pi_exact) <<  std::endl;
				/*printf("pi is approximately %.16f, Error is %.16f\n", pi, fabs(pi - pi_exact));*/
				endwtime = MPI_Wtime();
				printf("wall clock time = %f\n", endwtime-startwtime);
				fflush(stdout);
			}
		}
	}
	MPI_Finalize();
	return 0;
}
