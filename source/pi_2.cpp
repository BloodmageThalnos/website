#include "mpi.h"
#include <stdio.h>
#include <math.h>

long double f(long long a)
{
	return ((a&1)?4.0L:-4.0L)/(a+a-1);
}

int main(int argc, char *argv[])
{
	int myid, numprocs, done = 0;
	long long n, i;
	long double PI25DT = 3.141592653589793238462643;
	long double mypi, pi, h, sum, x;
	double startwtime = 0.0, endwtime;
	int  namelen;
	char processor_name[MPI_MAX_PROCESSOR_NAME];

	MPI_Init(&argc, &argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &myid);
	MPI_Get_processor_name(processor_name, &namelen);

	fprintf(stdout,"Process %d of %d is on %s\n",
		myid+1, numprocs, processor_name);
	fflush(stdout);

	while(!done) {
		if(myid == 0) {
			fprintf(stdout, "Enter the number of iterations: (0 quits) ");
			fflush(stdout);
			if(scanf("%lld", &n) != 1) {
				fprintf(stdout, "No number entered; quitting\n");
				n = 0;
			}
			startwtime = MPI_Wtime();
		}
		MPI_Bcast(&n, 1, MPI_LONG_LONG, 0, MPI_COMM_WORLD);
		if(n == 0)
			done = 1;
		else {
			sum = 0.0;
			for(i = myid + 1; i <= n; i += numprocs) {
				sum += f(i);
			}
			mypi = sum;
			MPI_Reduce(&mypi, &pi, 1, MPI_LONG_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

			if(myid == 0) {
				printf("pi is approximately %.16f, Error is %.16f\n",
					pi, fabs(pi - PI25DT));
				endwtime = MPI_Wtime();
				printf("wall clock time = %f\n", endwtime-startwtime);
				fflush(stdout);
			}
		}
	}
	MPI_Finalize();
	return 0;
}
