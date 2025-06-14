"""
Test script for the veta logging system.
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from veta.logger import setup_logging, get_logger, VetaLogger

class TestVetaLogging:
    """Test cases for the veta logging system."""
    
    def test_basic_logger_setup(self):
        """Test basic logger initialization."""
        logger = get_logger('test')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'veta.test'
    
    def test_main_logger(self):
        """Test getting the main logger."""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'veta'
    
    def test_custom_log_file(self):
        """Test logging to a custom file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(
                level='DEBUG',
                log_file=log_file,
                console_output=False,
                auto_generate_file=False
            )
            
            logger = get_logger('test_file')
            logger.info("Test message")
            
            # Check if file was created and contains our message
            assert os.path.exists(log_file)
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
                assert "test_file" in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_auto_generate_log_file(self):
        """Test auto-generation of log files."""
        # Setup with auto-generate
        setup_logging(auto_generate_file=True, console_output=False)
        
        logger = get_logger('test_auto')
        logger.info("Auto-generated test message")
        
        # Check that the main veta logger has handlers (child loggers don't have direct handlers)
        main_logger = get_logger()
        assert len(main_logger.handlers) > 0
    
    def test_different_log_levels(self):
        """Test different logging levels."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(
                level='DEBUG',
                log_file=log_file,
                console_output=False,
                file_level='DEBUG'
            )
            
            logger = get_logger('test_levels')
            logger.debug("Debug message")
            logger.info("Info message")  
            logger.warning("Warning message")
            logger.error("Error message")
            
            # Check all messages are in the file
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Debug message" in content
                assert "Info message" in content
                assert "Warning message" in content
                assert "Error message" in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_singleton_logger(self):
        """Test that VetaLogger follows singleton pattern."""
        logger1 = VetaLogger()
        logger2 = VetaLogger()
        assert logger1 is logger2
    
    def test_logger_formatting(self):
        """Test that log messages contain expected formatting elements."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(
                level='DEBUG',
                log_file=log_file,
                console_output=False
            )
            
            logger = get_logger('test_format')
            logger.info("Format test message")
            
            with open(log_file, 'r') as f:
                content = f.read()
                
                # Check for timestamp (YYYY-MM-DD HH:MM:SS format)
                assert any(char.isdigit() for char in content)
                
                # Check for log level
                assert "INFO" in content
                
                # Check for logger name
                assert "test_format" in content
                
                # Check for message
                assert "Format test message" in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

def test_integration_with_veta_components():
    """Test that veta components can use the logging system."""
    from veta.respondent import Respondent
    from veta.item import Item
    
    # Setup logging
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file = f.name
    
    try:
        setup_logging(
            level='DEBUG',
            log_file=log_file,
            console_output=False
        )
        
        # Create veta components which should generate logs
        respondent = Respondent(userid="test_user")
        item = Item("I feel happy", "She looks sad")
        respondent.add_item(item)
        
        # Check that logs were generated
        with open(log_file, 'r') as f:
            content = f.read()
            assert "respondent" in content.lower()
            assert "item" in content.lower()
            
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
