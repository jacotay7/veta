import pytest
import numpy as np
from unittest.mock import Mock, patch

from veta.scoring_modules.allsum import allsum
from veta.item import Item
from veta.wordlist import Wordlist


class TestAllsumScoringModule:
    """Test cases for the allsum scoring module"""

    def test_class_attributes(self):
        """Test class attributes are correctly set"""
        module = allsum()
        
        assert module.type == "per item"
        assert module.id == "allsum"

    def test_init_default_parameters(self):
        """Test initialization with default parameters"""
        module = allsum()
        
        assert module.id == "allsum"

    def test_init_with_language(self):
        """Test initialization with language parameter"""
        module = allsum(language='de')
        
        # Should not raise an error
        assert module.id == "allsum"

    def test_execute_basic(self, sample_wordlist_file):
        """Test execute method basic functionality"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should sum all scores: 1*4 + 1*2 = 6
            assert result == 6

    def test_execute_with_repeated_words(self, sample_wordlist_file):
        """Test execute method with repeated words"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("happy happy sad", "joyful")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([2, 1, 1]),  # frequency (happy appears twice)
                np.array(['happy', 'sad', 'joyful']),  # matching_words
                np.array([4, 2, 5])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should sum: 2*4 + 1*2 + 1*5 = 8 + 2 + 5 = 15
            assert result == 15

    def test_execute_no_matches(self, sample_wordlist_file):
        """Test execute method when no words match"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("xyz abc def", "uvw rst")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([]),  # frequency
                np.array([]),  # matching_words
                np.array([])   # scores
            )
            
            result = module.execute(item, wordlist)
            
            assert result == 0

    def test_execute_single_word_match(self, sample_wordlist_file):
        """Test execute method with single word match"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "xyz")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1]),  # frequency
                np.array(['happy']),  # matching_words
                np.array([4])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            assert result == 4

    def test_execute_high_frequency_word(self, sample_wordlist_file):
        """Test execute method with high frequency word"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("very very very happy", "")
        
        with patch.object(module, 'match_words') as mock_match:
            # Assume "very" is not in wordlist but "happy" is
            mock_match.return_value = (
                np.array([1]),  # frequency
                np.array(['happy']),  # matching_words
                np.array([4])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            assert result == 4

    def test_execute_combines_self_and_other(self, sample_wordlist_file):
        """Test that execute method combines self and other sentences"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            # Set up mock return value
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Verify match_words was called with combined sentence
            mock_match.assert_called_once()
            call_args = mock_match.call_args[0]
            expected_sentence = item.self_sentence + ' ' + item.other_sentence
            assert call_args[0] == expected_sentence

    def test_execute_empty_sentences(self, sample_wordlist_file):
        """Test execute method with empty sentences"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("", "")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([]),  # frequency
                np.array([]),  # matching_words
                np.array([])   # scores
            )
            
            result = module.execute(item, wordlist)
            
            assert result == 0

    def test_execute_with_zero_scores(self, sample_wordlist_file):
        """Test execute method with words that have zero scores"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("some words", "")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 2]),  # frequency
                np.array(['word1', 'word2']),  # matching_words
                np.array([0, 0])  # scores (all zeros)
            )
            
            result = module.execute(item, wordlist)
            
            assert result == 0

    def test_execute_with_negative_scores(self, sample_wordlist_file):
        """Test execute method with negative scores"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("some words", "")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['good', 'bad']),  # matching_words
                np.array([5, -2])  # scores (mixed positive/negative)
            )
            
            result = module.execute(item, wordlist)
            
            # Should sum: 1*5 + 1*(-2) = 3
            assert result == 3

    def test_execute_with_float_scores(self, sample_wordlist_file):
        """Test execute method with float scores"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("some words", "")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 2]),  # frequency
                np.array(['word1', 'word2']),  # matching_words
                np.array([2.5, 1.3])  # float scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should sum: 1*2.5 + 2*1.3 = 2.5 + 2.6 = 5.1
            assert abs(result - 5.1) < 0.001

    def test_execute_large_numbers(self, sample_wordlist_file):
        """Test execute method with large frequency and scores"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("words repeated many times", "")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([100, 50]),  # high frequency
                np.array(['word1', 'word2']),  # matching_words
                np.array([10, 20])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should sum: 100*10 + 50*20 = 1000 + 1000 = 2000
            assert result == 2000

    def test_inheritance_from_scoring_module(self):
        """Test that allsum properly inherits from ScoringModule"""
        module = allsum()
        
        # Should have parent class methods
        assert hasattr(module, 'is_full_word')
        assert hasattr(module, 'match_words')
        assert callable(module.is_full_word)
        assert callable(module.match_words)

    def test_execute_return_type(self, sample_wordlist_file):
        """Test that execute method returns the correct type"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Result should be numeric (int or float)
            assert isinstance(result, (int, float, np.integer, np.floating))

    def test_execute_with_complex_item(self, sample_wordlist_file):
        """Test execute method with complex item containing multiple emotions"""
        module = allsum()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item(
            "I feel extremely happy and joyful today because everything is wonderful",
            "She seems very sad and depressed about the situation"
        )
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1, 1, 1]),  # frequency
                np.array(['happy', 'joyful', 'sad', 'depressed']),  # matching_words
                np.array([4, 5, 2, 1])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should sum all: 4 + 5 + 2 + 1 = 12
            assert result == 12
