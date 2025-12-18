/*
 * Factorial Calculator
 *
 * Tests:
 * - Recursive function calls (if supported)
 * - Multiplication operations
 * - Conditional branches
 * - Return values
 *
 * Calculates: 7! = 5040
 * Result stored at memory address 0x2000
 */

#define RESULT_ADDR 0x2000

// Iterative factorial (safer for simple CPU)
int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

int main() {
    int n = 7;

    // Calculate factorial of 7
    int fact = factorial(n);

    // Store results
    int *result_ptr = (int *)RESULT_ADDR;
    *result_ptr = fact;          // fact(7) = 5040
    *(result_ptr + 1) = n;       // input value = 7

    // Calculate factorial of 5 for comparison
    int fact5 = factorial(5);
    *(result_ptr + 2) = fact5;   // fact(5) = 120

    // Calculate factorial of 10
    int fact10 = factorial(10);
    *(result_ptr + 3) = fact10;  // fact(10) = 3628800

    return 0;
}
