package com.example;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Unit test for the Calculator class that uses Addition and Subtraction classes.
 */
public class CalculatorTest {

    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    @Test
    void testAddition() {
        // Test a simple addition case
        int expected = 2;
        int actual = calculator.add(1, 1);
        assertEquals(expected, actual, "1 + 1 should equal 2");
    }

    @Test
    void testAdditionWithNegativeNumbers() {
        // Test addition with negative numbers
        assertEquals(-2, calculator.add(-1, -1), "Adding two negative numbers");
        assertEquals(0, calculator.add(-1, 1), "Adding negative and positive numbers");
    }

    @Test
    void testSubtraction() {
        // Test a simple subtraction case
        int expected = 2;
        int actual = calculator.subtract(5, 3);
        assertEquals(expected, actual, "5 - 3 should equal 2");
    }

    @Test
    void testSubtractionWithNegativeNumbers() {
        // Test subtraction with negative numbers
        assertEquals(4, calculator.subtract(2, -2), "Subtracting negative number");
        assertEquals(-4, calculator.subtract(-2, 2), "Subtracting from negative number");
    }

    @Test
    void testMultipleAddition() {
        // Test adding multiple numbers
        assertEquals(10, calculator.addMultiple(1, 2, 3, 4), "Adding multiple positive numbers");
        assertEquals(0, calculator.addMultiple(5, -3, -2), "Adding mixed positive and negative numbers");
    }

    @Test
    void testMultipleSubtraction() {
        // Test subtracting multiple numbers
        assertEquals(1, calculator.subtractMultiple(10, 2, 3, 4), "Subtracting multiple positive numbers");
        assertEquals(10, calculator.subtractMultiple(5, -3, -2), "Subtracting negative numbers (adding)");
    }

    @Test
    void testCalculatorWithDependencyInjection() {
        // Test calculator with injected dependencies
        Addition mockAddition = new Addition();
        Subtraction mockSubtraction = new Subtraction();
        Calculator calculatorWithDeps = new Calculator(mockAddition, mockSubtraction);
        
        assertEquals(4, calculatorWithDeps.add(2, 2), "Addition through dependency injection");
        assertEquals(1, calculatorWithDeps.subtract(3, 2), "Subtraction through dependency injection");
    }
}