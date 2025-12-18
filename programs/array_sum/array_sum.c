/*
 * Array Sum Program
 *
 * Tests:
 * - Array initialization
 * - Loops
 * - Arithmetic operations
 * - Memory load/store
 * - Conditional branches
 *
 * Result: Sum of numbers 1-10 = 55
 *         Stored at memory address 0x1000
 */

#define ARRAY_SIZE 10
#define RESULT_ADDR 0x1000

int main() {
    // Initialize array with values 1 to 10
    int array[ARRAY_SIZE];

    // Fill array
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = i + 1;
    }

    // Calculate sum
    int sum = 0;
    for (int i = 0; i < ARRAY_SIZE; i++) {
        sum += array[i];
    }

    // Store result at specific memory address
    int *result_ptr = (int *)RESULT_ADDR;
    *result_ptr = sum;

    // Store array size at next address
    *(result_ptr + 1) = ARRAY_SIZE;

    // Calculate and store average
    int average = sum / ARRAY_SIZE;
    *(result_ptr + 2) = average;

    return 0;
}
