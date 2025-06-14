import pytest
import numpy as np
import pandas as pd
import tempfile
import os
from unittest.mock import patch, MagicMock

from veta.wordlist import Wordlist, is_number


class TestWordlist:
    """Test cases for the Wordlist class"""

    def test_init_with_xlsx_file(self, sample_wordlist_file):
        """Test Wordlist initialization with xlsx file"""
        wordlist = Wordlist(sample_wordlist_file)
        
        assert wordlist.filename == sample_wordlist_file
        assert wordlist.creator == "veta"
        assert wordlist.name == "wordlist"
        assert wordlist.language == "en"
        assert len(wordlist.unique_id) == 26
        assert hasattr(wordlist, 'words')
        assert hasattr(wordlist, 'scores')
        assert hasattr(wordlist, 'subclasses')

    def test_init_with_custom_parameters(self, sample_wordlist_file):
        """Test Wordlist initialization with custom parameters"""
        wordlist = Wordlist(
            sample_wordlist_file,
            creator="test_creator",
            name="test_wordlist",
            language="de"
        )
        
        assert wordlist.creator == "test_creator"
        assert wordlist.name == "test_wordlist"
        assert wordlist.language == "de"

    def test_load_from_txt_file(self, sample_wordlist_txt_file):
        """Test loading wordlist from txt file"""
        wordlist = Wordlist(sample_wordlist_txt_file)
        
        assert len(wordlist.words) > 0
        assert len(wordlist.scores) > 0
        assert len(wordlist.words) == len(wordlist.scores)
        assert np.all(wordlist.subclasses == 0)  # Should be zeros for txt files

    def test_load_from_xlsx_file(self, sample_wordlist_file):
        """Test loading wordlist from xlsx file"""
        wordlist = Wordlist(sample_wordlist_file)
        
        assert len(wordlist.words) > 0
        assert len(wordlist.scores) > 0
        assert len(wordlist.subclasses) > 0
        assert len(wordlist.words) == len(wordlist.scores)
        assert len(wordlist.words) == len(wordlist.subclasses)

    def test_invalid_file_type(self, tmp_path):
        """Test handling of invalid file types"""
        invalid_file = tmp_path / "test.csv"
        invalid_file.write_text("word,score\nhappy,4\n")
        
        with pytest.raises(Exception, match="File Type not Supported"):
            Wordlist(str(invalid_file))

    def test_clean_wordlist_functionality(self, sample_wordlist_file):
        """Test that cleanWordlist method processes data correctly"""
        wordlist = Wordlist(sample_wordlist_file)
        
        # All words should be lowercase strings
        for word in wordlist.words:
            if isinstance(word, str):
                assert word.islower()

    def test_str_representation(self, sample_wordlist_file):
        """Test string representation of wordlist"""
        wordlist = Wordlist(sample_wordlist_file)
        str_repr = str(wordlist)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_words_scores_alignment(self, sample_wordlist_file):
        """Test that words and scores arrays are properly aligned"""
        wordlist = Wordlist(sample_wordlist_file)
        
        assert len(wordlist.words) == len(wordlist.scores)
        assert len(wordlist.words) == len(wordlist.subclasses)
        
        # Check that arrays are numpy arrays
        assert isinstance(wordlist.words, np.ndarray)
        assert isinstance(wordlist.scores, np.ndarray)
        assert isinstance(wordlist.subclasses, np.ndarray)

    def test_load_from_txt_method(self, sample_wordlist_txt_file):
        """Test the loadFromTxt method specifically"""
        wordlist = Wordlist(sample_wordlist_txt_file)
        
        # Verify that the data was loaded correctly
        assert 'happy' in wordlist.words
        assert 'sad' in wordlist.words
        
        # Find index of 'happy' and check its score
        happy_idx = np.where(wordlist.words == 'happy')[0]
        if len(happy_idx) > 0:
            assert wordlist.scores[happy_idx[0]] == 4

    def test_empty_wordlist_handling(self, tmp_path):
        """Test handling of empty wordlist files"""
        empty_file = tmp_path / "empty.xlsx"
        df = pd.DataFrame({'words': [], 'scores': []})
        df.to_excel(empty_file, index=False)
        
        wordlist = Wordlist(str(empty_file))
        assert len(wordlist.words) == 0
        assert len(wordlist.scores) == 0

    @patch('pandas.read_excel')
    def test_load_from_file_excel_error_handling(self, mock_read_excel, tmp_path):
        """Test error handling when Excel file cannot be read"""
        mock_read_excel.side_effect = Exception("File not found")
        
        test_file = tmp_path / "test.xlsx"
        test_file.touch()
        
        with pytest.raises(Exception):
            Wordlist(str(test_file))

    def test_wordlist_with_missing_subclasses(self, tmp_path):
        """Test wordlist with only words and scores (no subclasses column)"""
        file_path = tmp_path / "test_wordlist_no_subclasses.xlsx"
        df = pd.DataFrame({
            'words': ['happy', 'sad'],
            'scores': [4, 2]
        })
        df.to_excel(file_path, index=False)
        
        wordlist = Wordlist(str(file_path))
        assert len(wordlist.subclasses) == len(wordlist.words)
        assert np.all(wordlist.subclasses == 0)

    def test_add_word_method(self, sample_wordlist_file):
        """Test addWord method"""
        wordlist = Wordlist(sample_wordlist_file)
        initial_length = len(wordlist.words)
        
        # Add a new word
        wordlist.addWord("excited", 4.5, 1.0)
        
        # Check word was added
        assert len(wordlist.words) == initial_length + 1
        assert "excited" in wordlist.words
        assert 4.5 in wordlist.scores
        assert 1.0 in wordlist.subclasses

    def test_add_word_type_validation(self, sample_wordlist_file):
        """Test addWord with invalid types raises assertion error"""
        wordlist = Wordlist(sample_wordlist_file)
        
        # Test with invalid word type
        with pytest.raises(AssertionError):
            wordlist.addWord(123, 4.5, 1.0)  # word should be string
        
        # Test with invalid score type
        with pytest.raises(AssertionError):
            wordlist.addWord("excited", "4.5", 1.0)  # score should be float
        
        # Test with invalid subclass type
        with pytest.raises(AssertionError):
            wordlist.addWord("excited", 4.5, "1.0")  # subclass should be float

    def test_add_words_method(self, sample_wordlist_file):
        """Test addWords method"""
        wordlist = Wordlist(sample_wordlist_file)
        initial_length = len(wordlist.words)
        
        # Add multiple words
        new_words = ["excited", "thrilled", "delighted"]
        new_scores = [4.5, 5.0, 4.8]
        new_subclasses = [1.0, 1.0, 1.0]
        
        wordlist.addWords(new_words, new_scores, new_subclasses)
        
        # Check words were added
        assert len(wordlist.words) == initial_length + 3
        for word in new_words:
            assert word in wordlist.words

    def test_add_words_with_lists(self, sample_wordlist_file):
        """Test addWords method with list inputs"""
        wordlist = Wordlist(sample_wordlist_file)
        initial_length = len(wordlist.words)
        
        # Add words using lists (should be converted to numpy arrays)
        new_words = ["excited", "thrilled"]
        new_scores = [4.5, 5.0]
        new_subclasses = [1.0, 1.0]
        
        wordlist.addWords(new_words, new_scores, new_subclasses)
        
        # Check words were added
        assert len(wordlist.words) == initial_length + 2

    def test_add_words_without_subclasses(self, sample_wordlist_file):
        """Test addWords method without subclasses (should default to zeros)"""
        wordlist = Wordlist(sample_wordlist_file)
        initial_length = len(wordlist.words)
        
        # Add words without subclasses
        new_words = ["excited", "thrilled"]
        new_scores = [4.5, 5.0]
        
        wordlist.addWords(new_words, new_scores, None)
        
        # Check words were added with zero subclasses
        assert len(wordlist.words) == initial_length + 2

    def test_sort_wordlist_method(self, sample_wordlist_file):
        """Test sortWordlist method"""
        wordlist = Wordlist(sample_wordlist_file)
        
        # Add some words to make sorting more apparent
        wordlist.addWord("zebra", 1.0, 0.0)
        wordlist.addWord("apple", 5.0, 1.0)
        
        # Get words before sorting
        words_before = wordlist.words.copy()
        
        # Sort the wordlist
        wordlist.sortWordlist()
        
        # Check that words are now sorted
        assert np.array_equal(wordlist.words, np.sort(words_before))
        
        # Verify that scores and subclasses are still aligned
        apple_idx = np.where(wordlist.words == "apple")[0]
        zebra_idx = np.where(wordlist.words == "zebra")[0]
        
        if len(apple_idx) > 0:
            assert wordlist.scores[apple_idx[0]] == 5.0
            assert wordlist.subclasses[apple_idx[0]] == 1.0
        if len(zebra_idx) > 0:
            assert wordlist.scores[zebra_idx[0]] == 1.0
            assert wordlist.subclasses[zebra_idx[0]] == 0.0

class TestIsNumberFunction:
    """Test cases for the is_number utility function"""

    def test_is_number_integer(self):
        """Test is_number with integers"""
        assert is_number("123") == True
        assert is_number("-123") == True
        assert is_number("0") == True

    def test_is_number_float(self):
        """Test is_number with floats"""
        assert is_number("123.45") == True
        assert is_number("-123.45") == True
        assert is_number("0.0") == True

    def test_is_number_invalid(self):
        """Test is_number with invalid inputs"""
        assert is_number("abc") == False
        assert is_number("12.34.56") == False
        assert is_number("") == False
        assert is_number("   ") == False
        assert is_number("12a") == False

    def test_is_number_edge_cases(self):
        """Test is_number with edge cases"""
        assert is_number("  123  ") == True  # With whitespace
        assert is_number(".5") == False  # No leading digit
        assert is_number("5.") == False  # No trailing digit
        assert is_number("--5") == False  # Double negative
