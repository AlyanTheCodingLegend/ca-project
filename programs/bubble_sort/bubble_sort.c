/*
 * Bubble Sort
 *
 * Tests:
 * - Nested loops
 * - Conditional branches
 * - Array access
 * - Swap operations
 * - Comparisons
 *
 * Sorts array: [5, 2, 8, 1, 9, 3, 7, 4, 6]
 * Result: [1, 2, 3, 4, 5, 6, 7, 8, 9]
 * Stored at memory address 0x3000
 */

#define ARRAY_SIZE 9
#define RESULT_ADDR 0x3000

void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                // Swap elements
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    // Initialize unsorted array
    int array[ARRAY_SIZE] = {5, 2, 8, 1, 9, 3, 7, 4, 6};

    // Sort the array
    bubble_sort(array, ARRAY_SIZE);

    // Store sorted array to memory
    int *result_ptr = (int *)RESULT_ADDR;

    for (int i = 0; i < ARRAY_SIZE; i++) {
        result_ptr[i] = array[i];
    }

    // Store array size
    result_ptr[ARRAY_SIZE] = ARRAY_SIZE;

    // Calculate and store sum of sorted array
    int sum = 0;
    for (int i = 0; i < ARRAY_SIZE; i++) {
        sum += array[i];
    }
    result_ptr[ARRAY_SIZE + 1] = sum;  // Should be 45

    return 0;
}
