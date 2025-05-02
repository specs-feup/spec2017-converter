# Makefile for compiling SPEC benchmarks

# Find benchmark directories under benchspec/CPU named "src" or "build_base_mytest.0000"
BENCH_DIRS := $(shell find benchspec/CPU -type d \( -name src -o -name build_base_mytest.0000 \))
FAILED_MODULES_FILE := failed_modules.txt

.PHONY: all clean

all:
	@rm -f $(FAILED_MODULES_FILE)
	@echo "Compiling benchmarks..."
	@for dir in $(BENCH_DIRS); do \
		echo "-----------------------------------------------------"; \
		echo "Compiling benchmark in $$dir..."; \
		if $(MAKE) -C $$dir; then \
			echo "Compilation succeeded in $$dir"; \
		else \
			echo "Compilation FAILED in $$dir"; \
			echo "$$dir" >> $(FAILED_MODULES_FILE); \
		fi; \
	done; \
	if [ -f $(FAILED_MODULES_FILE) ]; then \
		echo "====================================================="; \
		echo "The following modules failed to compile:"; \
		cat $(FAILED_MODULES_FILE); \
		exit 1; \
	else \
		echo "====================================================="; \
		echo "All modules compiled successfully."; \
	fi

clean:
	@echo "Cleaning benchmarks..."
	@for dir in $(BENCH_DIRS); do \
		echo "Cleaning $$dir..."; \
		$(MAKE) -C $$dir clean; \
	done
	@rm -f $(FAILED_MODULES_FILE)
