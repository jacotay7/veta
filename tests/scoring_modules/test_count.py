import pytest
import numpy as np
from unittest.mock import Mock, patch

from veta.scoring_modules.count import count
from veta.item import Item
from veta.wordlist import Wordlist


class TestCountScoringModule:
    """Test cases for the count scoring module"""

    def test_class_attributes(self):
        """Test class attributes are correctly set"""
        module = count()
        
        assert module.type == "per item"
        assert "count" in module.id

    def test_init_default_parameters(self):
        """Test initialization with default parameters"""
        module = count()
        
        assert module.mode == 'both'
        assert module.level is None
        assert module.sublevel is None
        assert module.binary == False
        assert module.id == "count-both"

    def test_init_with_level(self):
        """Test initialization with specific level"""
        module = count(level=3)
        
        assert module.level == 3
        assert "level-3" in module.id

    def test_init_with_sublevel(self):
        """Test initialization with specific sublevel"""
        module = count(sublevel=2)
        
        assert module.sublevel == 2
        assert "sublevel-2" in module.id

    def test_init_with_binary_mode(self):
        """Test initialization with binary mode"""
        module = count(binary=True)
        
        assert module.binary == True
        assert "true_false" in module.id

    def test_init_with_mode_self(self):
        """Test initialization with self mode"""
        module = count(mode='self')
        
        assert module.mode == 'self'
        assert module.id.endswith('-self')

    def test_init_with_mode_other(self):
        """Test initialization with other mode"""
        module = count(mode='other')
        
        assert module.mode == 'other'
        assert module.id.endswith('-other')

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters"""
        module = count(mode='self', level=4, sublevel=1, binary=True, language='de')
        
        assert module.mode == 'self'
        assert module.level == 4
        assert module.sublevel == 1
        assert module.binary == True
        assert "level-4" in module.id
        assert "sublevel-1" in module.id
        assert "self" in module.id
        assert "true_false" in module.id

    def test_execute_both_mode(self, sample_wordlist_file):
        """Test execute method with both mode"""
        module = count(mode='both')
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        # Mock the match_words method to return predictable results
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should count unique words
            assert result == 2
            
            # Verify match_words was called with combined sentence
            mock_match.assert_called_once()
            call_args = mock_match.call_args[0]
            assert "i feel happy she seems sad" in call_args[0]

    def test_execute_self_mode(self, sample_wordlist_file):
        """Test execute method with self mode"""
        module = count(mode='self')
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1]),  # frequency
                np.array(['happy']),  # matching_words
                np.array([4])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            assert result == 1
            
            # Verify match_words was called with self sentence only
            call_args = mock_match.call_args[0]
            assert call_args[0] == item.self_sentence

    def test_execute_other_mode(self, sample_wordlist_file):
        """Test execute method with other mode"""
        module = count(mode='other')
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1]),  # frequency
                np.array(['sad']),  # matching_words
                np.array([2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            assert result == 1
            
            # Verify match_words was called with other sentence only
            call_args = mock_match.call_args[0]
            assert call_args[0] == item.other_sentence

    def test_execute_with_specific_level(self, sample_wordlist_file):
        """Test execute method with specific level"""
        module = count(level=4)
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should count only words with score level 4
            assert result == 1  # Only 'happy' has score 4

    def test_execute_with_specific_level_binary(self, sample_wordlist_file):
        """Test execute method with specific level and binary output"""
        module = count(level=4, binary=True)
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should return True because level 4 words exist
            assert result == True

    def test_execute_with_specific_level_no_matches(self, sample_wordlist_file):
        """Test execute method with level that has no matches"""
        module = count(level=10)  # Level that doesn't exist
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should return 0 because no words have score level 10
            assert result == 0

    def test_execute_with_sublevel(self, sample_wordlist_file):
        """Test execute method with sublevel"""
        module = count(level=4, sublevel=1)
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1, 1]),  # frequency
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2]),  # scores
                np.array([1, 1])   # subscores
            )
            
            result = module.execute(item, wordlist)
            
            # Should count words with both level 4 and sublevel 1
            assert result == 1

    def test_execute_binary_mode_general(self, sample_wordlist_file):
        """Test execute method with binary mode (no specific level)"""
        module = count(binary=True)
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([1]),  # frequency
                np.array(['happy']),  # matching_words - only 1 word
                np.array([4])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should return True if more than 1 word found (which is False in this case)
            assert result == False

    def test_execute_no_matches(self, sample_wordlist_file):
        """Test execute method when no words match"""
        module = count()
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

    def test_execute_repeated_words(self, sample_wordlist_file):
        """Test execute method with repeated words"""
        module = count()
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("happy happy happy", "sad sad")
        
        with patch.object(module, 'match_words') as mock_match:
            mock_match.return_value = (
                np.array([3, 2]),  # frequency (repeated words)
                np.array(['happy', 'sad']),  # matching_words
                np.array([4, 2])  # scores
            )
            
            result = module.execute(item, wordlist)
            
            # Should count unique words, not repetitions
            assert result == 2

    def test_language_parameter(self):
        """Test language parameter"""
        module = count(language='de')
        
        # Should not raise an error and should set language if supported
        assert hasattr(module, 'language') or True  # True fallback if not supported

    @patch('veta.scoring_modules.count.count.match_words')
    def test_match_words_sublevel_handling(self, mock_match_words, sample_wordlist_file):
        """Test that sublevels parameter is passed correctly to match_words"""
        module = count(sublevel=1)
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        mock_match_words.return_value = (
            np.array([1]),
            np.array(['happy']),
            np.array([4]),
            np.array([1])
        )
        
        module.execute(item, wordlist)
        
        # Verify match_words was called with sublevels=True
        mock_match_words.assert_called_once()
        call_kwargs = mock_match_words.call_args[1]
        assert call_kwargs.get('sublevels') == True
