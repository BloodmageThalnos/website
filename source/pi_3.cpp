#include "mpi.h"
#include <iostream>
#include <fstream>
#include <math.h>
#include <boost/multiprecision/cpp_bin_float.hpp>
using namespace boost::multiprecision;

#define PRECISION 2000
typedef number<cpp_bin_float<PRECISION> > pi_type;
typedef int a_type;

pi_type f(a_type a)
{
	return ((a&1)?pi_type(16):pi_type(-16))/(a+a-1)/pow(pi_type(5),a+a-1) -
		((a&1)?pi_type(4):pi_type(-4))/(a+a-1)/pow(pi_type(239), a+a-1);
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
			startwtime = MPI_Wtime();
		}
		MPI_Bcast(&n, sizeof(n), MPI_BYTE, 0, MPI_COMM_WORLD);
		if(!n) 
			done = 1;
		else {
			pi_type pi=0, sum=0;
			for(i = myid + 1; i <= n; i += numprocs) {
				sum += f(i);
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
				std::cout << "pi is approximately " << pi <<  std::endl;
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
