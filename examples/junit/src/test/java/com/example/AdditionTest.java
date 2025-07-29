package com.example;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Unit tests for the Addition class.
 */
public class AdditionTest {

    private Addition addition;

    @BeforeEach
    void setUp() {
        addition = new Addition();
    }

    @Test
    void testSimpleAddition() {
        // Test a simple addition case
        int expected = 2;
        int actual = addition.add(1, 1);
        assertEquals(expected, actual, "1 + 1 should equal 2");
    }

    @Test
    void testAdditionWithNegativeNumbers() {
        // Test addition with negative numbers
        assertEquals(-2, addition.add(-1, -1), "Adding two negative numbers");
        assertEquals(0, addition.add(-1, 1), "Adding negative and positive numbers");
    }

    @Test
    void testAdditionWithZero() {
        // Test addition with zero
        assertEquals(5, addition.add(5, 0), "Adding zero should return the original number");
        assertEquals(-3, addition.add(0, -3), "Adding zero to negative number");
    }

    @Test
    void testLargeNumbers() {
        // Test with larger numbers
        assertEquals(1000, addition.add(500, 500), "Adding large positive numbers");
        assertEquals(-1000, addition.add(-500, -500), "Adding large negative numbers");
    }

    @Test
    void testMultipleAddition() {
        // Test adding multiple numbers
        assertEquals(10, addition.addMultiple(1, 2, 3, 4), "Adding multiple positive numbers");
        assertEquals(0, addition.addMultiple(5, -3, -2), "Adding mixed positive and negative numbers");
        assertEquals(-6, addition.addMultiple(-1, -2, -3), "Adding multiple negative numbers");
    }

    @Test
    void testSingleNumberAddition() {
        // Test adding a single number
        assertEquals(5, addition.addMultiple(5), "Adding single number should return the number itself");
    }

    @Test
    void testEmptyAddition() {
        // Test adding no numbers
        assertEquals(0, addition.addMultiple(), "Adding no numbers should return 0");
    }
} 