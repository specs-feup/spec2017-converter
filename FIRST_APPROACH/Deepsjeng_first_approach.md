# Deepsjeng


## Remove certain occurrences like:

```cpp
#if !defined(SPEC)
const
#endif
```

These occurrences appear regularly and can be easily removed, leaving only:


```cpp
const

```

<aside>


In the header files, some occurrences need to be changed due to these modifications, such as:


```cpp
#if !defined(SPEC)
const BITBOARD RankAttacks(const BITBOARD occ, const unsigned int sq);
const BITBOARD FileAttacks(BITBOARD occ, const unsigned int sq);
const BITBOARD DiagonalAttacks(BITBOARD occ, const unsigned int sq);
const BITBOARD AntiDiagAttacks(BITBOARD occ, const unsigned int sq);
#else
BITBOARD RankAttacks(const BITBOARD occ, const unsigned int sq);
BITBOARD FileAttacks(BITBOARD occ, const unsigned int sq);
BITBOARD DiagonalAttacks(BITBOARD occ, const unsigned int sq);
BITBOARD AntiDiagAttacks(BITBOARD occ, const unsigned int sq);
#endif
```

to:

```cpp
const BITBOARD RankAttacks(const BITBOARD occ, const unsigned int sq);
const BITBOARD FileAttacks(BITBOARD occ, const unsigned int sq);
const BITBOARD DiagonalAttacks(BITBOARD occ, const unsigned int sq);
const BITBOARD AntiDiagAttacks(BITBOARD occ, const unsigned int sq);

```

since all the functions outside of SPEC are defined as `const`.



## Remove SPEC2017-specific behavior

`sjeng.cpp`

```cpp
/* SPEC version: take EPD testset from commandline */
    if (argc == 2) {
        run_epd_testsuite(&gamestate, &state, argv[1]);    
    } else {
        myprintf("Please specify the workfile.\n");
        return EXIT_FAILURE;
    }
```

`sjeng.h`

```cpp
#if defined(WIN32) || defined(WIN64) || defined(SPEC_WINDOWS)

```

to 

```cpp
#if defined(WIN32) || defined(WIN64)

```