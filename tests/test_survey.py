import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

from veta.survey import Survey, NumpyEncoder
from veta.respondent import Respondent
from veta.item import Item
from veta.wordlist import Wordlist


class TestNumpyEncoder:
    """Test cases for the NumpyEncoder class"""

    def test_encode_integer_types(self):
        """Test encoding numpy integer types"""
        encoder = NumpyEncoder()
        
        assert encoder.default(np.int32(42)) == 42
        assert encoder.default(np.int64(42)) == 42
        # Skip the abstract numpy.integer test as it can't be instantiated

    def test_encode_float_types(self):
        """Test encoding numpy float types"""
        encoder = NumpyEncoder()
        
        # Use approximate comparison for float32 due to precision differences
        result = encoder.default(np.float32(3.14))
        assert abs(result - 3.14) < 0.01
        
        assert encoder.default(np.float64(3.14)) == 3.14

    def test_encode_array(self):
        """Test encoding numpy arrays"""
        encoder = NumpyEncoder()
        
        arr = np.array([1, 2, 3])
        result = encoder.default(arr)
        assert result == [1, 2, 3]

    def test_encode_bool(self):
        """Test encoding numpy boolean"""
        encoder = NumpyEncoder()
        
        assert encoder.default(np.bool_(True)) == True
        assert encoder.default(np.bool_(False)) == False

    def test_encode_unsupported_type(self):
        """Test encoding unsupported types falls back to default"""
        encoder = NumpyEncoder()
        
        # Should raise TypeError for unsupported types
        with pytest.raises(TypeError):
            encoder.default(object())


class TestSurvey:
    """Test cases for the Survey class"""

    def test_init_basic(self):
        """Test basic Survey initialization"""
        survey = Survey()
        
        assert isinstance(survey.respondents, list)
        assert len(survey.respondents) == 0
        assert survey.wordlist is None
        assert survey.cols == [0, 1, 2]
        assert survey.num_item_cols == 0
        assert isinstance(survey.summary, dict)
        assert np.array_equal(survey.header, np.array(["ID", "Self", "Other"]))

    def test_init_with_wordlist_file(self, sample_wordlist_file):
        """Test Survey initialization with wordlist file"""
        survey = Survey(wordlist_file=sample_wordlist_file)
        
        assert survey.wordlist is not None
        assert isinstance(survey.wordlist, Wordlist)

    def test_init_with_invalid_wordlist_file(self):
        """Test Survey initialization with invalid wordlist file"""
        survey = Survey(wordlist_file=123)  # Non-string
        
        assert survey.wordlist is None

    def test_add_respondent(self):
        """Test adding respondent to survey"""
        survey = Survey()
        respondent = Respondent(userid="test_user")
        
        survey.add_respondent(respondent)
        
        assert len(survey.respondents) == 1
        assert survey.respondents[0] == respondent

    def test_add_multiple_respondents(self):
        """Test adding multiple respondents"""
        survey = Survey()
        
        respondents = [
            Respondent(userid="user1"),
            Respondent(userid="user2"),
            Respondent(userid="user3")
        ]
        
        for respondent in respondents:
            survey.add_respondent(respondent)
        
        assert len(survey.respondents) == 3
        for i, respondent in enumerate(respondents):
            assert survey.respondents[i] == respondent

    def test_add_wordlist(self, sample_wordlist_file):
        """Test adding wordlist to survey"""
        survey = Survey()
        wordlist = Wordlist(sample_wordlist_file)
        
        survey.add_wordlist(wordlist)
        
        assert survey.wordlist == wordlist

    def test_add_wordlist_propagates_to_respondents(self, sample_wordlist_file):
        """Test that adding wordlist propagates to existing respondents"""
        survey = Survey()
        respondent = Respondent(userid="test_user")
        survey.add_respondent(respondent)
        
        wordlist = Wordlist(sample_wordlist_file)
        survey.add_wordlist(wordlist)
        
        assert respondent.wordlist == wordlist

    def test_str_representation_empty(self):
        """Test string representation of empty survey"""
        survey = Survey()
        
        str_repr = str(survey)
        assert str_repr == ""

    def test_str_representation_with_respondents(self):
        """Test string representation with respondents"""
        survey = Survey()
        
        respondent1 = Respondent(userid="user1")
        respondent1.add_item("I feel happy", "She seems sad")
        
        respondent2 = Respondent(userid="user2")
        respondent2.add_item("I am excited", "He is angry")
        
        survey.add_respondent(respondent1)
        survey.add_respondent(respondent2)
        
        str_repr = str(survey)
        
        assert "Respondent ID user1:" in str_repr
        assert "Respondent ID user2:" in str_repr

    def test_from_vertical_layout_basic(self, sample_survey_data):
        """Test processing vertical layout data"""
        survey = Survey()
        
        # Mock the cols attribute to match expected columns
        survey.cols = [0, 1, 2, 3, 4]
        survey.num_item_cols = 2
        
        survey.from_vertical_layout(sample_survey_data)
        
        # Should have processed the data
        assert hasattr(survey, 'data')
        assert hasattr(survey, 'header')

    def test_from_vertical_layout_with_totals(self):
        """Test processing vertical layout with totals rows"""
        survey = Survey()
        
        # Create test data with NaN values indicating totals
        data = np.array([
            ['ID', 'Self', 'Other', 'Score1'],
            ['user1', 'I feel happy', 'She is sad', ''],
            [np.nan, '', '', 5],  # Totals row
        ])
        
        survey.cols = [0, 1, 2, 3]
        survey.num_item_cols = 1
        
        survey.from_vertical_layout(data)
        
        # Should have created respondents
        assert len(survey.respondents) >= 1

    def test_load_from_file(self, tmp_path, sample_survey_data):
        """Test loading survey from Excel file using from_file method"""
        # Create temporary Excel file
        excel_file = tmp_path / "test_survey.xlsx"
        df = pd.DataFrame(sample_survey_data[1:], columns=sample_survey_data[0])
        df.to_excel(excel_file, index=False)
        
        survey = Survey()
        survey.from_file(str(excel_file))
        
        # Should have loaded data
        assert hasattr(survey, 'data')

    def test_load_from_file_nonexistent(self):
        """Test loading from nonexistent Excel file"""
        survey = Survey()
        
        with pytest.raises((FileNotFoundError, Exception)):
            survey.from_file("nonexistent_file.xlsx")

    def test_score_method_exists(self):
        """Test that score method exists"""
        survey = Survey()
        
        assert hasattr(survey, 'score')
        assert callable(survey.score)

    def test_score_all_respondents(self, sample_wordlist_file):
        """Test scoring all respondents"""
        survey = Survey()
        wordlist = Wordlist(sample_wordlist_file)
        survey.add_wordlist(wordlist)
        
        # Add respondents with items
        respondent1 = Respondent(userid="user1")
        respondent1.add_item("I feel happy", "She seems sad")
        
        respondent2 = Respondent(userid="user2")
        respondent2.add_item("I am joyful", "He is angry")
        
        survey.add_respondent(respondent1)
        survey.add_respondent(respondent2)
        
        # Mock scoring module
        mock_module = Mock()
        mock_module.id = "test_score"
        mock_module.type = "per item"
        mock_module.execute.return_value = 5
        
        survey.score(mock_module)
        
        # All items should have been scored
        for respondent in survey.respondents:
            for item in respondent.items:
                assert "test_score" in item.scores
                assert "index" in item.scores  # This is always added by add_item

    def test_summary_statistics_method_exists(self):
        """Test that summary statistics methods exist"""
        survey = Survey()
        
        # Check for various summary methods that might exist
        methods_to_check = ['get_summary', 'calculate_statistics', 'analyze']
        
        for method_name in methods_to_check:
            if hasattr(survey, method_name):
                assert callable(getattr(survey, method_name))

    def test_export_functionality(self):
        """Test export functionality if it exists"""
        survey = Survey()
        
        # Check for export methods
        export_methods = ['to_excel', 'to_csv', 'export_data', 'save']
        
        for method_name in export_methods:
            if hasattr(survey, method_name):
                assert callable(getattr(survey, method_name))

    def test_data_processing_pipeline(self, sample_wordlist_file):
        """Test complete data processing pipeline"""
        survey = Survey(wordlist_file=sample_wordlist_file)
        
        # Add respondent
        respondent = Respondent(userid="test_user")
        respondent.add_item("I feel happy", "She seems sad")
        survey.add_respondent(respondent)
        
        # Verify pipeline components
        assert survey.wordlist is not None
        assert len(survey.respondents) == 1
        assert len(survey.respondents[0].items) == 1
        assert survey.respondents[0].wordlist == survey.wordlist

    @patch('openpyxl.load_workbook')
    def test_excel_loading_error_handling(self, mock_load_workbook):
        """Test error handling in Excel file loading"""
        mock_load_workbook.side_effect = Exception("File corrupted")
        
        survey = Survey()
        
        with pytest.raises(Exception):
            survey.from_file("test.xlsx")

    def test_cols_attribute_modification(self):
        """Test modification of cols attribute"""
        survey = Survey()
        
        original_cols = survey.cols.copy()
        survey.cols = [0, 1, 2, 3, 4, 5]
        
        assert survey.cols != original_cols
        assert len(survey.cols) == 6

    def test_num_item_cols_modification(self):
        """Test modification of num_item_cols attribute"""
        survey = Survey()
        
        assert survey.num_item_cols == 0
        
        survey.num_item_cols = 5
        assert survey.num_item_cols == 5

    def test_header_modification(self):
        """Test modification of header attribute"""
        survey = Survey()
        
        original_header = survey.header.copy()
        new_header = np.array(["ID", "Self", "Other", "Score1", "Score2"])
        survey.header = new_header
        
        assert not np.array_equal(survey.header, original_header)
        assert np.array_equal(survey.header, new_header)

    def test_summary_dict_operations(self):
        """Test operations on summary dictionary"""
        survey = Survey()
        
        assert isinstance(survey.summary, dict)
        assert len(survey.summary) == 0
        
        # Add some summary data
        survey.summary["total_respondents"] = 10
        survey.summary["avg_score"] = 4.5
        
        assert survey.summary["total_respondents"] == 10
        assert survey.summary["avg_score"] == 4.5

    def test_respondents_list_operations(self):
        """Test various operations on respondents list"""
        survey = Survey()
        
        # Add respondents
        respondents = [Respondent(userid=f"user{i}") for i in range(3)]
        
        for respondent in respondents:
            survey.add_respondent(respondent)
        
        assert len(survey.respondents) == 3
        
        # Test indexing
        assert survey.respondents[0].userid == "user0"
        assert survey.respondents[-1].userid == "user2"
        
        # Test iteration
        userids = [r.userid for r in survey.respondents]
        assert userids == ["user0", "user1", "user2"]
