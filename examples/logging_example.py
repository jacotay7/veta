#!/usr/bin/env python3
"""
Example script demonstrating the veta logging system.

This script shows how to initialize and use the comprehensive logging
system throughout the veta package.
"""

# Import veta components and logging
from veta import setup_logging, get_logger
from veta.survey import Survey
from veta.respondent import Respondent
from veta.item import Item

def main():
    """Main function demonstrating veta logging capabilities."""
    
    # Example 1: Basic logging setup with auto-generated log file
    print("=== Example 1: Basic Logging Setup ===")
    setup_logging(
        level='INFO',
        console_level='INFO',
        file_level='DEBUG',
        auto_generate_file=True
    )
    
    # Get a logger for this example
    logger = get_logger('example')
    logger.info("Starting veta logging demonstration")
    
    # Example 2: Create a survey and demonstrate logging
    print("\n=== Example 2: Survey Operations with Logging ===")
    survey = Survey()
    logger.info("Created new survey")
    
    # Add some respondents
    for i in range(3):
        respondent = Respondent(userid=f"user_{i:03d}")
        
        # Add some items to each respondent
        respondent.add_item("I feel happy today", "She seems sad")
        respondent.add_item("I am excited", "He looks worried")
        
        survey.add_respondent(respondent)
    
    logger.info(f"Survey now has {len(survey.respondents)} respondents")
    
    # Example 3: Different log levels demonstration
    print("\n=== Example 3: Different Log Levels ===")
    logger.debug("This is a debug message - detailed information")
    logger.info("This is an info message - general information")
    logger.warning("This is a warning message - something needs attention")
    logger.error("This is an error message - something went wrong")
    
    # Example 4: Module-specific loggers
    print("\n=== Example 4: Module-specific Loggers ===")
    item_logger = get_logger('item_processing')
    respondent_logger = get_logger('respondent_analysis')
    
    item_logger.info("Processing individual items")
    respondent_logger.info("Analyzing respondent data")
    
    # Example 5: Demonstrate error handling with logging
    print("\n=== Example 5: Error Handling with Logging ===")
    try:
        # This will create a warning/error in the wordlist loading
        item = Item("Test sentence")
        # Attempting to score without wordlist should generate logs
        logger.warning("Attempting operation that may fail...")
        
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        logger.debug("This would contain detailed stack trace information")
    
    logger.info("Veta logging demonstration completed")
    print("\n=== Logging Demonstration Complete ===")
    print("Check the generated log file for detailed debug information!")

def demonstrate_custom_logging():
    """Demonstrate custom logging configuration."""
    print("\n=== Custom Logging Configuration Example ===")
    
    # Setup logging with custom file and levels
    setup_logging(
        level='DEBUG',
        log_file='./custom_veta_analysis.log',
        console_output=True,
        file_level='DEBUG',
        console_level='WARNING',  # Only show warnings and errors in console
        auto_generate_file=False
    )
    
    custom_logger = get_logger('custom_analysis')
    
    # These will appear in the log file but not console (due to console_level='WARNING')
    custom_logger.debug("Detailed debug info - only in file")
    custom_logger.info("General info - only in file")
    
    # This will appear in both console and file
    custom_logger.warning("Warning message - appears in both console and file")
    
    print("Custom logging example complete - check 'custom_veta_analysis.log'")

if __name__ == "__main__":
    main()
    demonstrate_custom_logging()
