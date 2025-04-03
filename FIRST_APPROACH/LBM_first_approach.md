# LBM

## Remove easily identifiable SPEC-related traces such as:

```c
#if (defined(_OPENMP) || defined(SPEC_OPENMP)) && !defined(SPEC_SUPPRESS_OPENMP) && !defined(SPEC_AUTO_SUPPRESS_OPENMP)
#include <omp.h>
#endif
```

or  

```c
#ifndef SPEC
	printf( "LBM_allocateGrid: allocated %.1f MByte\n",
	        size / (1024.0*1024.0) );
#endif
```

## Change conditions such as:

```c
#if !defined(SPEC)
		int i;
#else
               size_t i;
#endif
```

to 

```c
	int i;
```

or 

```c
#if !defined(SPEC)
#include <sys/times.h>
#endif

```

to

```c
#include <sys/times.h>

```

