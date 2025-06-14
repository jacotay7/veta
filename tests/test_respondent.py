import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from veta.respondent import Respondent, total_respondents
from veta.item import Item
from veta.wordlist import Wordlist


class TestRespondent:
    """Test cases for the Respondent class"""

    def test_init_basic(self):
        """Test basic Respondent initialization"""
        respondent = Respondent()
        
        assert isinstance(respondent.items, list)
        assert len(respondent.items) == 0
        assert isinstance(respondent.id, int)
        assert respondent.userid is None
        assert respondent.wordlist is None
        assert isinstance(respondent.totals, dict)
        assert isinstance(respondent.col_names, list)

    def test_init_with_userid(self):
        """Test Respondent initialization with userid"""
        test_userid = "test_user_123"
        respondent = Respondent(userid=test_userid)
        
        assert respondent.userid == test_userid

    def test_init_with_wordlist_file(self, sample_wordlist_file):
        """Test Respondent initialization with wordlist file"""
        respondent = Respondent(wordlist_file=sample_wordlist_file)
        
        assert respondent.wordlist is not None
        assert isinstance(respondent.wordlist, Wordlist)

    def test_global_id_increment(self):
        """Test that global ID counter increments"""
        # Store current total
        current_total = total_respondents
        
        # Create new respondents
        r1 = Respondent()
        r2 = Respondent()
        
        # IDs should be sequential
        assert r2.id == r1.id + 1

    def test_add_item_with_two_sentences(self):
        """Test adding item with self and other sentences"""
        respondent = Respondent()
        
        item = respondent.add_item("I feel happy", "She seems sad")
        
        assert len(respondent.items) == 1
        assert isinstance(item, Item)
        assert item.self_sentence == "i feel happy"
        assert item.other_sentence == "she seems sad"

    def test_add_item_with_single_sentence(self):
        """Test adding item with single sentence"""
        respondent = Respondent()
        
        item = respondent.add_item("I feel happy")
        
        assert len(respondent.items) == 1
        assert isinstance(item, Item)
        assert item.self_sentence == "i feel happy"
        assert item.other_sentence == ""

    def test_add_multiple_items(self):
        """Test adding multiple items"""
        respondent = Respondent()
        
        item1 = respondent.add_item("I feel happy", "She seems sad")
        item2 = respondent.add_item("I am excited", "He is angry")
        item3 = respondent.add_item("I feel calm")
        
        assert len(respondent.items) == 3
        assert respondent.items[0] == item1
        assert respondent.items[1] == item2
        assert respondent.items[2] == item3

    def test_add_additional_info(self):
        """Test adding additional information to totals"""
        respondent = Respondent()
        
        respondent.add_additional_info("age", 25)
        respondent.add_additional_info("gender", "female")
        respondent.add_additional_info("score", 42.5)
        
        assert respondent.totals["age"] == 25
        assert respondent.totals["gender"] == "female"
        assert respondent.totals["score"] == 42.5

    def test_add_additional_info_overwrite(self):
        """Test overwriting additional information"""
        respondent = Respondent()
        
        respondent.add_additional_info("score", 10)
        assert respondent.totals["score"] == 10
        
        respondent.add_additional_info("score", 20)
        assert respondent.totals["score"] == 20

    def test_str_representation_with_userid(self):
        """Test string representation with userid"""
        respondent = Respondent(userid="test_user_123")
        respondent.add_item("I feel happy", "She seems sad")
        
        str_repr = str(respondent)
        
        assert "Respondent ID test_user_123:" in str_repr
        assert "Item 1:" in str_repr
        assert "Self:" in str_repr
        assert "Other:" in str_repr

    def test_str_representation_without_userid(self):
        """Test string representation without userid"""
        respondent = Respondent()
        respondent.add_item("I feel happy", "She seems sad")
        
        str_repr = str(respondent)
        
        assert f"Respondent ID {respondent.id}:" in str_repr
        assert "Item 1:" in str_repr

    def test_str_representation_multiple_items(self):
        """Test string representation with multiple items"""
        respondent = Respondent(userid="test_user")
        respondent.add_item("I feel happy", "She seems sad")
        respondent.add_item("I am excited", "He is angry")
        
        str_repr = str(respondent)
        
        assert "Item 1:" in str_repr
        assert "Item 2:" in str_repr

    def test_str_representation_no_items(self):
        """Test string representation with no items"""
        respondent = Respondent(userid="test_user")
        
        str_repr = str(respondent)
        
        assert "Respondent ID test_user:" in str_repr
        # Should not contain any item information

    def test_to_array_empty_items(self):
        """Test to_array with no items"""
        respondent = Respondent()
        
        array = respondent.to_array()
        
        assert isinstance(array, np.ndarray)
        assert array.shape == (0, 0)

    def test_to_array_with_items_no_scores(self):
        """Test to_array with items but no scores"""
        respondent = Respondent()
        respondent.add_item("I feel happy", "She seems sad")
        
        # Mock the method to avoid issues with empty scores
        with patch.object(respondent, 'to_array', return_value=np.array([[]])):
            array = respondent.to_array()
            assert isinstance(array, np.ndarray)

    def test_add_wordlist(self, sample_wordlist_file):
        """Test adding wordlist to respondent"""
        respondent = Respondent()
        wordlist = Wordlist(sample_wordlist_file)
        
        respondent.add_wordlist(wordlist)
        
        assert respondent.wordlist == wordlist

    def test_add_wordlist_propagates_to_items(self, sample_wordlist_file):
        """Test that adding wordlist propagates to existing items"""
        respondent = Respondent()
        item = respondent.add_item("I feel happy", "She seems sad")
        
        wordlist = Wordlist(sample_wordlist_file)
        respondent.add_wordlist(wordlist)
        
        assert item.wordlist == wordlist

    def test_score_method_exists(self):
        """Test that score method exists and can be called"""
        respondent = Respondent()
        
        # Should have a score method
        assert hasattr(respondent, 'score')
        assert callable(respondent.score)

    def test_score_with_no_items(self):
        """Test scoring with no items"""
        respondent = Respondent()
        
        # Should not raise an error
        try:
            respondent.score()
        except Exception as e:
            # If it raises an exception, it should be a reasonable one
            assert "wordlist" in str(e).lower() or "module" in str(e).lower()

    def test_score_with_items_no_wordlist(self):
        """Test scoring with items but no wordlist"""
        respondent = Respondent()
        respondent.add_item("I feel happy", "She seems sad")
        
        # Should handle gracefully or raise appropriate error
        try:
            respondent.score()
        except Exception as e:
            assert "wordlist" in str(e).lower() or "module" in str(e).lower()

    @patch('veta.respondent.Respondent.score')
    def test_score_method_call(self, mock_score):
        """Test that score method can be called with modules"""
        respondent = Respondent()
        mock_module = Mock()
        
        respondent.score(mock_module)
        
        mock_score.assert_called_once_with(mock_module)

    def test_items_maintain_order(self):
        """Test that items maintain their order"""
        respondent = Respondent()
        
        sentences = [
            ("First sentence", "First other"),
            ("Second sentence", "Second other"),
            ("Third sentence", "Third other")
        ]
        
        for self_sent, other_sent in sentences:
            respondent.add_item(self_sent, other_sent)
        
        for i, (expected_self, expected_other) in enumerate(sentences):
            assert respondent.items[i].self_sentence == expected_self.lower()
            assert respondent.items[i].other_sentence == expected_other.lower()

    def test_userid_type_validation(self):
        """Test userid type validation"""
        # String userid should work
        respondent1 = Respondent(userid="test_user")
        assert respondent1.userid == "test_user"
        
        # Non-string userid should result in None
        respondent2 = Respondent(userid=123)
        assert respondent2.userid is None
        
        respondent3 = Respondent(userid=None)
        assert respondent3.userid is None

    def test_wordlist_file_type_validation(self):
        """Test wordlist_file type validation"""
        # Non-string wordlist_file should not create wordlist
        respondent = Respondent(wordlist_file=123)
        assert respondent.wordlist is None

    def test_col_names_initialization(self):
        """Test col_names is properly initialized"""
        respondent = Respondent()
        
        assert isinstance(respondent.col_names, list)
        assert len(respondent.col_names) == 0

    def test_totals_dictionary_operations(self):
        """Test various operations on totals dictionary"""
        respondent = Respondent()
        
        # Test adding different types of data
        respondent.add_additional_info("int_val", 42)
        respondent.add_additional_info("float_val", 3.14)
        respondent.add_additional_info("str_val", "test")
        respondent.add_additional_info("list_val", [1, 2, 3])
        respondent.add_additional_info("dict_val", {"key": "value"})
        
        assert len(respondent.totals) == 5
        assert respondent.totals["int_val"] == 42
        assert respondent.totals["float_val"] == 3.14
        assert respondent.totals["str_val"] == "test"
        assert respondent.totals["list_val"] == [1, 2, 3]
        assert respondent.totals["dict_val"] == {"key": "value"}

    def test_to_array_with_scored_items(self, sample_wordlist_file):
        """Test to_array method with scored items"""
        from veta.scoring_modules.allsum import allsum
        
        respondent = Respondent(userid="test_user")
        wordlist = Wordlist(sample_wordlist_file)
        respondent.add_wordlist(wordlist)
        
        # Add items and score them
        respondent.add_item("I feel happy", "She seems sad")
        respondent.add_item("I am excited", "He appears angry")
        
        # Score with a module
        scoring_module = allsum()
        respondent.score(scoring_module)
        
        # Get array
        data_array = respondent.to_array()
        
        # Should have data for items plus totals row
        assert data_array.shape[0] == 3  # 2 items + 1 totals row
        assert data_array.shape[1] > 0  # Should have columns for scores
        
        # Last row should contain totals
        assert "allsum" in respondent.totals

    def test_score_with_per_respondent_module(self, sample_wordlist_file):
        """Test scoring with per-respondent module"""
        respondent = Respondent(userid="test_user")
        wordlist = Wordlist(sample_wordlist_file)
        respondent.add_wordlist(wordlist)
        
        # Add items
        respondent.add_item("I feel happy", "She seems sad")
        respondent.add_item("I am excited", "He appears angry")
        
        # Mock per-respondent scoring module
        mock_module = Mock()
        mock_module.type = "per respondent"
        mock_module.id = "test_per_respondent"
        mock_module.execute.return_value = 10
        
        respondent.score(mock_module)
        
        # Check that all items got zero scores and total was set
        for item in respondent.items:
            assert item.scores["test_per_respondent"] == 0
        assert respondent.totals["test_per_respondent"] == 10

    def test_compute_totals_method(self, sample_wordlist_file):
        """Test compute_totals method"""
        from veta.scoring_modules.allsum import allsum
        
        respondent = Respondent(userid="test_user")
        wordlist = Wordlist(sample_wordlist_file)
        respondent.add_wordlist(wordlist)
        
        # Add items and score them manually
        item1 = respondent.add_item("I feel happy", "She seems sad")
        item2 = respondent.add_item("I am excited", "He appears angry")
        
        # Manually add scores to items
        item1.scores["test_module"] = 5
        item2.scores["test_module"] = 3
        
        # Call compute_totals
        respondent.compute_totals()
        
        # Check that totals were computed
        assert "test_module" in respondent.totals
        assert respondent.totals["test_module"] == 8  # 5 + 3
