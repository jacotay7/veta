import pytest
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch

from veta.survey import Survey
from veta.respondent import Respondent
from veta.item import Item
from veta.wordlist import Wordlist
from veta.scoring_modules.allsum import allsum
from veta.scoring_modules.count import count


@pytest.mark.integration
class TestVetaIntegration:
    """Integration tests for the entire veta package workflow"""

    def test_full_workflow_with_wordlist(self, sample_wordlist_file):
        """Test complete workflow from survey creation to scoring"""
        # Create survey with wordlist
        survey = Survey(wordlist_file=sample_wordlist_file)
        
        # Add respondents with items
        respondent1 = Respondent(userid="user_001")
        respondent1.add_item("I feel happy and joyful", "She seems sad")
        
        respondent2 = Respondent(userid="user_002")
        respondent2.add_item("I am angry", "He appears depressed")
        
        survey.add_respondent(respondent1)
        survey.add_respondent(respondent2)
        
        # Score with multiple modules
        allsum_module = allsum()
        count_module = count()
        
        survey.score(allsum_module, count_module)
        
        # Verify results
        assert len(survey.respondents) == 2
        
        for respondent in survey.respondents:
            assert len(respondent.items) > 0
            for item in respondent.items:
                assert "allsum" in item.scores
                assert "count-both" in item.scores

    def test_survey_from_data_matrix(self, sample_survey_data, sample_wordlist_file):
        """Test creating survey from data matrix"""
        survey = Survey(wordlist_file=sample_wordlist_file)
        survey.cols = [0, 1, 2, 3, 4]
        survey.num_item_cols = 2
        
        # Process the data
        survey.from_vertical_layout(sample_survey_data)
        
        # Should have created respondents and items
        assert len(survey.respondents) > 0

    def test_respondent_scoring_workflow(self, sample_wordlist_file):
        """Test respondent-level scoring workflow"""
        wordlist = Wordlist(sample_wordlist_file)
        
        # Create respondent with multiple items
        respondent = Respondent(userid="test_user")
        respondent.add_wordlist(wordlist)
        
        items_data = [
            ("I feel happy", "She seems sad"),
            ("I am excited", "He appears angry"),
            ("I feel joyful", "She looks depressed")
        ]
        
        for self_text, other_text in items_data:
            respondent.add_item(self_text, other_text)
        
        # Score all items
        scoring_module = allsum()
        respondent.score(scoring_module)
        
        # Verify all items were scored
        for item in respondent.items:
            assert "allsum" in item.scores
            assert isinstance(item.scores["allsum"], (int, float, np.integer, np.floating))

    def test_wordlist_creation_and_usage(self, tmp_path):
        """Test creating and using a custom wordlist"""
        # Create custom wordlist file
        wordlist_data = [
            ["word", "score", "subclass"],
            ["fantastic", 5, 1],
            ["terrible", 1, 2],
            ["amazing", 5, 1],
            ["awful", 1, 2]
        ]
        
        wordlist_file = tmp_path / "custom_wordlist.xlsx"
        import pandas as pd
        df = pd.DataFrame(wordlist_data[1:], columns=wordlist_data[0])
        df.to_excel(wordlist_file, index=False)
        
        # Create wordlist and use it
        wordlist = Wordlist(str(wordlist_file))
        
        # Create item and score it
        item = Item("I feel fantastic", "It was terrible")
        
        scoring_module = allsum()
        score = scoring_module.execute(item, wordlist)
        
        # Should have matched words and calculated score
        assert isinstance(score, (int, float, np.integer, np.floating))

    def test_multiple_scoring_modules(self, sample_wordlist_file):
        """Test using multiple scoring modules on the same data"""
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy and joyful", "She seems very sad")
        
        # Test different scoring modules
        modules = [
            allsum(),
            count(),
            count(mode='self'),
            count(mode='other'),
            count(binary=True)
        ]
        
        scores = {}
        for module in modules:
            score = module.execute(item, wordlist)
            scores[module.id] = score
        
        # Should have different scores for different modules
        assert len(scores) == len(modules)
        
        # Verify score types
        for module_id, score in scores.items():
            if "true_false" in module_id:
                assert isinstance(score, (bool, np.bool_))
            else:
                assert isinstance(score, (int, float, np.integer, np.floating))

    def test_survey_export_workflow(self, sample_wordlist_file):
        """Test survey data export workflow"""
        survey = Survey(wordlist_file=sample_wordlist_file)
        
        # Add respondents
        for i in range(3):
            respondent = Respondent(userid=f"user_{i:03d}")
            respondent.add_item(f"I feel emotion {i}", f"They feel something {i}")
            survey.add_respondent(respondent)
        
        # Score all respondents
        scoring_module = allsum()
        survey.score(scoring_module)
        
        # Test string representation
        survey_str = str(survey)
        assert len(survey_str) > 0
        assert "user_000" in survey_str
        assert "user_001" in survey_str
        assert "user_002" in survey_str

    @pytest.mark.slow
    def test_large_dataset_processing(self, sample_wordlist_file):
        """Test processing a larger dataset"""
        survey = Survey(wordlist_file=sample_wordlist_file)
        
        # Create many respondents
        emotions = ["happy", "sad", "angry", "joyful", "depressed"]
        
        for i in range(50):  # Create 50 respondents
            respondent = Respondent(userid=f"user_{i:04d}")
            
            # Add multiple items per respondent
            for j in range(5):
                emotion = emotions[j % len(emotions)]
                respondent.add_item(
                    f"I feel {emotion} today",
                    f"Others seem {emotion} too"
                )
            
            survey.add_respondent(respondent)
        
        # Score all
        scoring_modules = [allsum(), count()]
        survey.score(*scoring_modules)
        
        # Verify all were processed
        assert len(survey.respondents) == 50
        
        for respondent in survey.respondents:
            assert len(respondent.items) == 5
            for item in respondent.items:
                assert "allsum" in item.scores
                assert "count-both" in item.scores

    def test_error_handling_workflow(self, tmp_path):
        """Test error handling in various workflow scenarios"""
        # Test with invalid wordlist file
        with pytest.raises(Exception):
            Wordlist("nonexistent_file.xlsx")
        
        # Test with corrupted wordlist
        bad_file = tmp_path / "bad_wordlist.xlsx"
        bad_file.write_text("not a real excel file")
        
        with pytest.raises(Exception):
            Wordlist(str(bad_file))
        
        # Test scoring without wordlist
        survey = Survey()
        respondent = Respondent()
        respondent.add_item("I feel happy", "She seems sad")
        survey.add_respondent(respondent)
        
        # Should handle missing wordlist gracefully or raise appropriate error
        scoring_module = allsum()
        try:
            survey.score(scoring_module)
        except Exception as e:
            assert "wordlist" in str(e).lower() or len(str(e)) > 0

    def test_data_consistency_workflow(self, sample_wordlist_file):
        """Test data consistency throughout the workflow"""
        survey = Survey(wordlist_file=sample_wordlist_file)
        
        # Add respondent
        respondent = Respondent(userid="consistency_test")
        original_item = respondent.add_item("I feel happy", "She seems sad")
        survey.add_respondent(respondent)
        
        # Verify data consistency
        assert survey.respondents[0] == respondent
        assert respondent.items[0] == original_item
        assert respondent.wordlist == survey.wordlist
        
        # Score and verify consistency maintained
        scoring_module = allsum()
        survey.score(scoring_module)
        
        assert survey.respondents[0] == respondent
        assert respondent.items[0] == original_item
        assert "allsum" in original_item.scores

    def test_wordlist_propagation(self, sample_wordlist_file):
        """Test that wordlists propagate correctly through the hierarchy"""
        # Create survey with wordlist
        survey = Survey(wordlist_file=sample_wordlist_file)
        
        # Add respondent and item
        respondent = Respondent(userid="propagation_test")
        item = respondent.add_item("I feel happy", "She seems sad")
        survey.add_respondent(respondent)
        
        # Wordlist should have propagated
        assert survey.wordlist is not None
        assert respondent.wordlist == survey.wordlist
        assert item.wordlist == survey.wordlist
        
        # Test adding wordlist after structure is created
        new_survey = Survey()
        new_respondent = Respondent(userid="new_test")
        new_item = new_respondent.add_item("I am excited", "He is calm")
        new_survey.add_respondent(new_respondent)
        
        # Add wordlist - should propagate
        wordlist = Wordlist(sample_wordlist_file)
        new_survey.add_wordlist(wordlist)
        
        assert new_survey.wordlist == wordlist
        assert new_respondent.wordlist == wordlist
        assert new_item.wordlist == wordlist
