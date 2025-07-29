package com.example;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Unit tests for the Subtraction class.
 */
public class SubtractionTest {

    private Subtraction subtraction;

    @BeforeEach
    void setUp() {
        subtraction = new Subtraction();
    }

    @Test
    void testSimpleSubtraction() {
        // Test a simple subtraction case
        int expected = 2;
        int actual = subtraction.subtract(5, 3);
        assertEquals(expected, actual, "5 - 3 should equal 2");
    }

    @Test
    void testSubtractionWithNegativeNumbers() {
        // Test subtraction with negative numbers
        assertEquals(4, subtraction.subtract(2, -2), "Subtracting negative number");
        assertEquals(-4, subtraction.subtract(-2, 2), "Subtracting from negative number");
        assertEquals(0, subtraction.subtract(-2, -2), "Subtracting negative from negative");
    }

    @Test
    void testSubtractionWithZero() {
        // Test subtraction with zero
        assertEquals(5, subtraction.subtract(5, 0), "Subtracting zero should return the original number");
        assertEquals(-3, subtraction.subtract(0, 3), "Subtracting from zero");
    }

    @Test
    void testLargeNumbers() {
        // Test with larger numbers
        assertEquals(500, subtraction.subtract(1000, 500), "Subtracting large positive numbers");
        assertEquals(-500, subtraction.subtract(-1000, -500), "Subtracting large negative numbers");
    }

    @Test
    void testMultipleSubtraction() {
        // Test subtracting multiple numbers
        assertEquals(1, subtraction.subtractMultiple(10, 2, 3, 4), "Subtracting multiple positive numbers");
        assertEquals(10, subtraction.subtractMultiple(5, -3, -2), "Subtracting negative numbers (adding)");
        assertEquals(6, subtraction.subtractMultiple(0, -1, -2, -3), "Subtracting negative numbers from zero");
    }

    @Test
    void testSingleNumberSubtraction() {
        // Test subtracting a single number
        assertEquals(5, subtraction.subtractMultiple(5, 0), "Subtracting zero should return the original number");
    }

    @Test
    void testNoSubtraction() {
        // Test subtracting no numbers
        assertEquals(10, subtraction.subtractMultiple(10), "Subtracting no numbers should return the original number");
    }

    @Test
    void testSubtractionResultingInZero() {
        // Test cases where subtraction results in zero
        assertEquals(0, subtraction.subtract(5, 5), "Subtracting same number should equal zero");
        assertEquals(0, subtraction.subtractMultiple(10, 3, 4, 3), "Multiple subtraction resulting in zero");
    }
} 