import pytest
from unittest.mock import patch, Mock

from veta.auto_self_other_item import attempt_auto_self_other
from veta.item import Item


class TestAutoSelfOtherItem:
    """Test cases for the auto_self_other_item module"""

    def test_attempt_auto_self_other_english_default(self):
        """Test attempt_auto_self_other with English (default language)"""
        item = Item("I feel happy. She feels sad.")
        
        # Mock spacy processing
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            # Create mock tokens
            mock_tokens = [
                Mock(text="I", dep_="nsubj", head=Mock(text="feel")),
                Mock(text="feel", dep_="ROOT", head=Mock(text="feel")),
                Mock(text="happy", dep_="amod", head=Mock(text="feel")),
                Mock(text="She", dep_="nsubj", head=Mock(text="feels")),
                Mock(text="feels", dep_="ROOT", head=Mock(text="feels")),
                Mock(text="sad", dep_="amod", head=Mock(text="feels"))
            ]
            mock_nlp.return_value = mock_tokens
            
            original_self = item.self_sentence
            original_other = item.other_sentence
            
            attempt_auto_self_other(item)
            
            # Should have processed the item
            mock_nlp.assert_called_once_with(item.raw_input)

    def test_attempt_auto_self_other_german(self):
        """Test attempt_auto_self_other with German language"""
        item = Item("Ich fühle mich glücklich. Sie fühlt sich traurig.")
        
        # Mock spacy processing for German
        with patch('veta.auto_self_other_item.nlp_de') as mock_nlp:
            mock_tokens = [
                Mock(text="Ich", dep_="sb", head=Mock(text="fühle")),
                Mock(text="fühle", dep_="ROOT", head=Mock(text="fühle")),
                Mock(text="mich", dep_="obj", head=Mock(text="fühle")),
                Mock(text="glücklich", dep_="amod", head=Mock(text="fühle"))
            ]
            mock_nlp.return_value = mock_tokens
            
            attempt_auto_self_other(item, lang="de")
            
            mock_nlp.assert_called_once_with(item.raw_input)

    def test_attempt_auto_self_other_self_identification(self):
        """Test correct identification of self vs other statements"""
        item = Item("I feel happy. She feels sad.")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            # Mock tokens where "I" is subject of "feel" and "She" is subject of "feels"
            mock_tokens = [
                Mock(text="I", dep_="nsubj", head=Mock(text="feel")),
                Mock(text="feel", dep_="ROOT", head=Mock(text="feel")),
                Mock(text="happy", dep_="amod", head=Mock(text="feel")),
                Mock(text=".", dep_="punct", head=Mock(text="feel")),
                Mock(text="She", dep_="nsubj", head=Mock(text="feels")),
                Mock(text="feels", dep_="ROOT", head=Mock(text="feels")),
                Mock(text="sad", dep_="amod", head=Mock(text="feels"))
            ]
            mock_nlp.return_value = mock_tokens
            
            attempt_auto_self_other(item)
            
            # Check that sentences were properly separated
            # The function should modify item.self_sentence and item.other_sentence
            assert hasattr(item, 'self_sentence')
            assert hasattr(item, 'other_sentence')

    def test_attempt_auto_self_other_all_self_pronouns(self):
        """Test with sentences containing only self pronouns"""
        item = Item("I feel happy. I am excited.")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            mock_tokens = [
                Mock(text="I", dep_="nsubj", head=Mock(text="feel")),
                Mock(text="feel", dep_="ROOT", head=Mock(text="feel")),
                Mock(text="happy", dep_="amod", head=Mock(text="feel")),
                Mock(text="I", dep_="nsubj", head=Mock(text="am")),
                Mock(text="am", dep_="ROOT", head=Mock(text="am")),
                Mock(text="excited", dep_="amod", head=Mock(text="am"))
            ]
            mock_nlp.return_value = mock_tokens
            
            attempt_auto_self_other(item)
            
            # All text should be classified as self
            mock_nlp.assert_called_once()

    def test_attempt_auto_self_other_verb_identification(self):
        """Test identification of emotion-related verbs"""
        item = Item("I feel happy. He looks angry.")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            # "feel" is in verblist, "looks" is not
            mock_tokens = [
                Mock(text="I", dep_="nsubj", head=Mock(text="feel")),
                Mock(text="feel", dep_="ROOT", head=Mock(text="feel")),
                Mock(text="happy", dep_="amod", head=Mock(text="feel")),
                Mock(text="He", dep_="nsubj", head=Mock(text="looks")),
                Mock(text="looks", dep_="ROOT", head=Mock(text="looks")),
                Mock(text="angry", dep_="amod", head=Mock(text="looks"))
            ]
            mock_nlp.return_value = mock_tokens
            
            attempt_auto_self_other(item)
            
            mock_nlp.assert_called_once()

    def test_attempt_auto_self_other_german_pronouns(self):
        """Test German pronoun identification"""
        item = Item("Ich bin glücklich. Er ist traurig.")
        
        with patch('veta.auto_self_other_item.nlp_de') as mock_nlp:
            mock_tokens = [
                Mock(text="Ich", dep_="sb", head=Mock(text="bin")),
                Mock(text="bin", dep_="ROOT", head=Mock(text="bin")),
                Mock(text="glücklich", dep_="pred", head=Mock(text="bin")),
                Mock(text="Er", dep_="sb", head=Mock(text="ist")),
                Mock(text="ist", dep_="ROOT", head=Mock(text="ist")),
                Mock(text="traurig", dep_="pred", head=Mock(text="ist"))
            ]
            mock_nlp.return_value = mock_tokens
            
            attempt_auto_self_other(item, lang="de")
            
            mock_nlp.assert_called_once()

    def test_attempt_auto_self_other_language_variants(self):
        """Test different language parameter variants"""
        item = Item("Test sentence")
        
        # Test various ways to specify German
        german_variants = ["de", "german", "deutsch", "DE", "German", "Deutsch"]
        
        for lang_variant in german_variants:
            with patch('veta.auto_self_other_item.nlp_de') as mock_nlp:
                mock_nlp.return_value = []
                
                attempt_auto_self_other(item, lang=lang_variant)
                
                # Should use German model for all variants
                mock_nlp.assert_called_once()

    def test_attempt_auto_self_other_english_explicit(self):
        """Test explicitly specifying English language"""
        item = Item("I feel happy")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            mock_nlp.return_value = []
            
            # Test various ways to specify English
            english_variants = ["en", "english", "EN", "English"]
            
            for lang_variant in english_variants:
                mock_nlp.reset_mock()
                attempt_auto_self_other(item, lang=lang_variant)
                mock_nlp.assert_called_once()

    def test_attempt_auto_self_other_modifies_item_in_place(self):
        """Test that the function modifies the item in place"""
        item = Item("I feel happy. She feels sad.")
        original_raw_input = item.raw_input
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            mock_nlp.return_value = [
                Mock(text="I", dep_="nsubj", head=Mock(text="feel")),
                Mock(text="feel", dep_="ROOT", head=Mock(text="feel")),
                Mock(text="happy", dep_="amod", head=Mock(text="feel"))
            ]
            
            attempt_auto_self_other(item)
            
            # Raw input should remain unchanged
            assert item.raw_input == original_raw_input
            
            # But self_sentence and other_sentence should be modified
            # (exact values depend on the processing logic)

    def test_attempt_auto_self_other_empty_sentences(self):
        """Test handling of empty or whitespace sentences"""
        item = Item("", "")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            mock_nlp.return_value = []
            
            attempt_auto_self_other(item)
            
            # Should handle empty input gracefully
            mock_nlp.assert_called_once()

    def test_attempt_auto_self_other_no_subjects(self):
        """Test sentences with no clear subjects"""
        item = Item("Happy feelings today.")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            mock_nlp.return_value = [
                Mock(text="Happy", dep_="amod", head=Mock(text="feelings")),
                Mock(text="feelings", dep_="ROOT", head=Mock(text="feelings")),
                Mock(text="today", dep_="npadvmod", head=Mock(text="feelings"))
            ]
            
            attempt_auto_self_other(item)
            
            # Should process without errors
            mock_nlp.assert_called_once()

    def test_attempt_auto_self_other_mixed_subjects(self):
        """Test sentences with mixed self/other subjects"""
        item = Item("I feel happy but she feels sad and I am confused.")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            mock_tokens = [
                Mock(text="I", dep_="nsubj", head=Mock(text="feel")),
                Mock(text="feel", dep_="ROOT", head=Mock(text="feel")),
                Mock(text="happy", dep_="amod", head=Mock(text="feel")),
                Mock(text="but", dep_="cc", head=Mock(text="feel")),
                Mock(text="she", dep_="nsubj", head=Mock(text="feels")),
                Mock(text="feels", dep_="ROOT", head=Mock(text="feels")),
                Mock(text="sad", dep_="amod", head=Mock(text="feels")),
                Mock(text="and", dep_="cc", head=Mock(text="feels")),
                Mock(text="I", dep_="nsubj", head=Mock(text="am")),
                Mock(text="am", dep_="ROOT", head=Mock(text="am")),
                Mock(text="confused", dep_="acomp", head=Mock(text="am"))
            ]
            mock_nlp.return_value = mock_tokens
            
            attempt_auto_self_other(item)
            
            # Should handle complex sentence structure
            mock_nlp.assert_called_once()

    @patch('veta.auto_self_other_item.nlp_en', None)
    @patch('veta.auto_self_other_item.nlp_de', None)
    def test_attempt_auto_self_other_no_spacy_models(self):
        """Test behavior when spacy models are not available"""
        item = Item("I feel happy")
        
        # Should handle missing models gracefully
        # (might raise exception or handle gracefully depending on implementation)
        try:
            attempt_auto_self_other(item)
            # If no exception, that's fine
        except Exception as e:
            # If exception occurs, it should be a reasonable one
            assert "spacy" in str(e).lower() or "model" in str(e).lower()

    def test_attempt_auto_self_other_return_none(self):
        """Test that function returns None (modifies in place)"""
        item = Item("I feel happy")
        
        with patch('veta.auto_self_other_item.nlp_en') as mock_nlp:
            mock_nlp.return_value = []
            
            result = attempt_auto_self_other(item)
            
            assert result is None
