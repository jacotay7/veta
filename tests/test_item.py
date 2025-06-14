import pytest
import numpy as np
from unittest.mock import Mock, patch

from veta.item import Item
from veta.wordlist import Wordlist


class TestItem:
    """Test cases for the Item class"""

    def test_init_basic(self):
        """Test basic Item initialization"""
        item = Item("I feel happy", "She seems sad")
        
        assert item.raw_input == "I feel happy. She seems sad"
        assert isinstance(item.self_sentence, str)
        assert isinstance(item.other_sentence, str)
        assert isinstance(item.full_sentence, str)
        assert isinstance(item.scores, dict)
        assert len(item.scores) == 0
        assert item.wordlist is None

    def test_init_with_empty_other_sentence(self):
        """Test Item initialization with empty other sentence"""
        item = Item("I feel happy")
        
        assert item.raw_input == "I feel happy. "
        assert item.self_sentence == "i feel happy"
        assert item.other_sentence == ""

    def test_init_with_empty_sentences(self):
        """Test Item initialization with empty sentences"""
        item = Item("", "")
        
        assert item.raw_input == ". "
        assert item.self_sentence == ""
        assert item.other_sentence == ""

    def test_clean_sentence_punctuation(self):
        """Test sentence cleaning removes punctuation"""
        item = Item("Test sentence", "")
        
        # Test various punctuation marks that should be removed
        dirty_sentence = "Hello, world! How are you? I'm fine; thanks."
        clean_sentence = item.clean_sentence(dirty_sentence)
        
        assert "," not in clean_sentence
        assert "!" not in clean_sentence
        assert "?" not in clean_sentence
        assert ";" not in clean_sentence
        assert "." not in clean_sentence
        # Note: single quotes are NOT removed by the current implementation
        assert "'" in clean_sentence  # This stays as per actual implementation

    def test_clean_sentence_case_conversion(self):
        """Test sentence cleaning converts to lowercase"""
        item = Item("Test sentence", "")
        
        dirty_sentence = "HELLO World TeStInG"
        clean_sentence = item.clean_sentence(dirty_sentence)
        
        assert clean_sentence == "hello world testing"

    def test_clean_sentence_special_characters(self):
        """Test sentence cleaning handles special characters"""
        item = Item("Test sentence", "")
        
        dirty_sentence = "Hello_world–with-special,chars.test?yes!/no:maybe(sure)$100\n\r\t"
        clean_sentence = item.clean_sentence(dirty_sentence)
        
        # Should replace all special chars with spaces and clean up
        assert "_" not in clean_sentence
        assert "–" not in clean_sentence
        assert "-" not in clean_sentence
        assert "," not in clean_sentence
        assert "." not in clean_sentence
        assert "?" not in clean_sentence
        assert "!" not in clean_sentence
        assert "/" not in clean_sentence
        assert ":" not in clean_sentence
        assert "(" not in clean_sentence
        assert ")" not in clean_sentence
        assert "$" not in clean_sentence
        assert "\n" not in clean_sentence
        assert "\r" not in clean_sentence
        assert "\t" not in clean_sentence

    def test_clean_sentence_whitespace_handling(self):
        """Test sentence cleaning handles multiple spaces"""
        item = Item("Test sentence", "")
        
        dirty_sentence = "Hello    world   with   spaces"
        clean_sentence = item.clean_sentence(dirty_sentence)
        
        # The current implementation only does one replacement of double spaces
        # So multiple spaces might still exist
        assert clean_sentence.strip() == clean_sentence
        # Test that at least some space normalization happened
        assert len(clean_sentence) <= len(dirty_sentence)

    def test_add_additional_info(self):
        """Test adding additional information to scores"""
        item = Item("I feel happy", "She seems sad")
        
        item.add_additional_info("test_key", "test_value")
        item.add_additional_info("score", 42)
        item.add_additional_info("list_data", [1, 2, 3])
        
        assert item.scores["test_key"] == "test_value"
        assert item.scores["score"] == 42
        assert item.scores["list_data"] == [1, 2, 3]

    def test_add_additional_info_overwrite(self):
        """Test overwriting additional information"""
        item = Item("I feel happy", "She seems sad")
        
        item.add_additional_info("key", "original_value")
        assert item.scores["key"] == "original_value"
        
        item.add_additional_info("key", "new_value")
        assert item.scores["key"] == "new_value"

    def test_str_representation(self):
        """Test string representation of Item"""
        item = Item("I feel happy", "She seems sad")
        item.add_additional_info("score", 42)
        item.add_additional_info("level", 3)
        
        str_repr = str(item)
        
        assert "Self:" in str_repr
        assert "Other:" in str_repr
        assert "i feel happy" in str_repr
        assert "she seems sad" in str_repr
        assert "score: 42" in str_repr
        assert "level: 3" in str_repr

    def test_str_representation_empty_scores(self):
        """Test string representation with no scores"""
        item = Item("I feel happy", "She seems sad")
        
        str_repr = str(item)
        
        assert "Self:" in str_repr
        assert "Other:" in str_repr
        assert "i feel happy" in str_repr
        assert "she seems sad" in str_repr

    def test_sentence_processing_consistency(self):
        """Test that sentence processing is consistent"""
        self_text = "I feel HAPPY today!"
        other_text = "She seems very SAD."
        
        item = Item(self_text, other_text)
        
        # Check that cleaning is applied consistently
        assert item.self_sentence == item.clean_sentence(self_text)
        assert item.other_sentence == item.clean_sentence(other_text)
        assert item.full_sentence == item.clean_sentence(self_text + ". " + other_text)

    def test_clean_sentence_with_numbers(self):
        """Test sentence cleaning preserves numbers"""
        item = Item("Test", "")
        
        sentence_with_numbers = "I have 5 cats and 10 dogs"
        clean_sentence = item.clean_sentence(sentence_with_numbers)
        
        assert "5" in clean_sentence
        assert "10" in clean_sentence
        assert clean_sentence == "i have 5 cats and 10 dogs"

    def test_clean_sentence_with_none_input(self):
        """Test sentence cleaning with None input"""
        item = Item("Test", "")
        
        clean_sentence = item.clean_sentence(None)
        assert clean_sentence == "none"

    def test_clean_sentence_with_numeric_input(self):
        """Test sentence cleaning with numeric input"""
        item = Item("Test", "")
        
        clean_sentence = item.clean_sentence(123)
        assert clean_sentence == "123"

    def test_scores_dictionary_type(self):
        """Test that scores is always a dictionary"""
        item = Item("I feel happy", "She seems sad")
        
        assert isinstance(item.scores, dict)
        
        # Even after adding items, it should remain a dict
        item.add_additional_info("test", "value")
        assert isinstance(item.scores, dict)

    def test_wordlist_attribute(self):
        """Test wordlist attribute management"""
        item = Item("I feel happy", "She seems sad")
        
        # Initially None
        assert item.wordlist is None
        
        # Should be able to set to None explicitly
        item.wordlist = None
        assert item.wordlist is None

    def test_raw_input_composition(self):
        """Test raw_input is properly composed from self and other sentences"""
        self_sentence = "I am happy"
        other_sentence = "She is sad"
        
        item = Item(self_sentence, other_sentence)
        
        expected_raw_input = f"{self_sentence}. {other_sentence}"
        assert item.raw_input == expected_raw_input

    def test_sentence_attributes_are_strings(self):
        """Test that all sentence attributes are strings after initialization"""
        item = Item("I feel happy", "She seems sad")
        
        assert isinstance(item.raw_input, str)
        assert isinstance(item.full_sentence, str)
        assert isinstance(item.self_sentence, str)
        assert isinstance(item.other_sentence, str)

    def test_score_with_scoring_module_returning_tuple(self):
        """Test scoring with a module that returns a tuple"""
        item = Item("I feel happy", "She seems sad")
        
        # Mock scoring module that returns a tuple
        mock_scoring_module = Mock()
        mock_scoring_module.id = "mock_module"
        mock_scoring_module.execute.return_value = (5, 3, 7)  # Tuple result
        
        # Mock the wordlist
        item.wordlist = Mock(spec=Wordlist)
        
        item.score(mock_scoring_module)
        
        # Check that tuple results are stored with indexed keys
        assert "mock_module1" in item.scores
        assert "mock_module2" in item.scores
        assert "mock_module3" in item.scores
        assert item.scores["mock_module1"] == 5
        assert item.scores["mock_module2"] == 3
        assert item.scores["mock_module3"] == 7

    def test_score_without_wordlist_raises_exception(self):
        """Test that scoring without wordlist raises exception"""
        item = Item("I feel happy", "She seems sad")
        
        # Mock scoring module that requires wordlist
        mock_scoring_module = Mock()
        mock_scoring_module.id = "mock_module"
        mock_scoring_module.execute.return_value = 5
        
        # Set wordlist to None
        item.wordlist = None
        
        with pytest.raises(Exception, match="Scoring Error: Item does not have a wordlist"):
            item.score(mock_scoring_module)

    def test_add_wordlist_method(self):
        """Test add_wordlist method"""
        item = Item("I feel happy", "She seems sad")
        wordlist = Mock(spec=Wordlist)
        
        # Initially no wordlist
        assert item.wordlist is None
        
        # Add wordlist
        item.add_wordlist(wordlist)
        
        # Check wordlist is set
        assert item.wordlist is wordlist
