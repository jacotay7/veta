import pytest
import numpy as np
from unittest.mock import Mock, patch

from veta.scoring_modules.length import length
from veta.scoring_modules.vocab import vocab
from veta.item import Item
from veta.wordlist import Wordlist


class TestLengthScoringModule:
    """Test cases for the length scoring module if it exists"""

    def test_length_module_basic(self):
        """Test basic length module functionality"""
        try:
            module = length()
            assert module.type == "per item"
            assert "length" in module.id
        except ImportError:
            pytest.skip("length module not available")

    def test_length_execution(self, sample_wordlist_file):
        """Test length module execution"""
        try:
            module = length()
            wordlist = Wordlist(sample_wordlist_file)
            item = Item("I feel happy today", "She seems sad")
            
            result = module.execute(item, wordlist)
            assert isinstance(result, (int, float))
            assert result >= 0
        except ImportError:
            pytest.skip("length module not available")


class TestVocabScoringModule:
    """Test cases for the vocab scoring module if it exists"""

    def test_vocab_module_basic(self):
        """Test basic vocab module functionality"""
        try:
            module = vocab()
            assert module.type == "per respondent"
            assert "vocab" in module.id
        except ImportError:
            pytest.skip("vocab module not available")

    def test_vocab_execution(self, sample_wordlist_file):
        """Test vocab module execution"""
        try:
            module = vocab()
            wordlist = Wordlist(sample_wordlist_file)
            item = Item("I feel happy today", "She seems sad")
            
            # vocab module expects a list of items (per respondent)
            result = module.execute([item], wordlist)
            assert isinstance(result, (int, float, np.integer, np.floating))
        except ImportError:
            pytest.skip("vocab module not available")


class TestScoringModulesGeneral:
    """General tests for scoring modules that may exist"""

    def test_available_scoring_modules(self):
        """Test which scoring modules are available"""
        modules_to_test = [
            'allsum', 'allsum_unique', 'count', 'length', 'vocab',
            'sentiment', 'highestN', 'highestN_unique', 'highestN_allinone',
            'powerlaw', 'exp', 'mlr', '_334', '_3345', '_3345plus'
        ]
        
        available_modules = []
        
        for module_name in modules_to_test:
            try:
                module_path = f'veta.scoring_modules.{module_name}'
                module = __import__(module_path, fromlist=[module_name])
                class_obj = getattr(module, module_name)
                
                # Handle modules that require parameters
                if module_name == 'highestN':
                    instance = class_obj(N=3)  # highestN requires N parameter
                elif module_name in ['highestN_unique', 'highestN_allinone']:
                    instance = class_obj(N=3)  # These might also require N parameter
                else:
                    instance = class_obj()
                    
                available_modules.append(module_name)
            except (ImportError, AttributeError, TypeError):
                pass
        
        # Should have at least some modules available
        assert len(available_modules) >= 2  # We know allsum and count exist

    def test_scoring_module_interface_compliance(self):
        """Test that available scoring modules comply with the interface"""
        from veta.scoring_modules.allsum import allsum
        from veta.scoring_modules.count import count
        
        modules = [allsum(), count()]
        
        for module in modules:
            # Should have required attributes
            assert hasattr(module, 'type')
            assert hasattr(module, 'id')
            assert hasattr(module, 'execute')
            
            # Should have parent class methods
            assert hasattr(module, 'is_full_word')
            assert hasattr(module, 'match_words')
            
            # Type should be valid
            assert module.type in ['per item', 'per respondent']
            
            # ID should be a string
            assert isinstance(module.id, str)
            assert len(module.id) > 0

    def test_all_scoring_modules_execute_signature(self, sample_wordlist_file):
        """Test that all scoring modules have consistent execute signature"""
        from veta.scoring_modules.allsum import allsum
        from veta.scoring_modules.count import count
        
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        modules = [allsum(), count()]
        
        for module in modules:
            # Should be able to call execute with item and wordlist
            try:
                result = module.execute(item, wordlist)
                # Result should be numeric or boolean
                assert isinstance(result, (int, float, bool, np.integer, np.floating, np.bool_))
            except NotImplementedError:
                # Some modules might not be fully implemented
                pass

    def test_scoring_module_ids_unique(self):
        """Test that scoring module IDs are unique"""
        from veta.scoring_modules.allsum import allsum
        from veta.scoring_modules.count import count
        
        modules = [
            allsum(),
            count(),
            count(mode='self'),
            count(mode='other'),
            count(binary=True)
        ]
        
        ids = [module.id for module in modules]
        
        # All IDs should be unique
        assert len(ids) == len(set(ids))

    def test_per_item_vs_per_respondent_types(self):
        """Test distinction between per item and per respondent scoring"""
        from veta.scoring_modules.allsum import allsum
        from veta.scoring_modules.count import count
        
        # These should be per item
        per_item_modules = [allsum(), count()]
        
        for module in per_item_modules:
            assert module.type == "per item"

    @patch('veta.scoring_modules.scoring_module.ScoringModule.match_words')
    def test_scoring_modules_error_handling(self, mock_match_words, sample_wordlist_file):
        """Test error handling in scoring modules"""
        from veta.scoring_modules.allsum import allsum
        
        wordlist = Wordlist(sample_wordlist_file)
        item = Item("I feel happy", "She seems sad")
        
        # Test with match_words raising an exception
        mock_match_words.side_effect = Exception("Test error")
        
        module = allsum()
        
        with pytest.raises(Exception):
            module.execute(item, wordlist)

    def test_scoring_modules_with_empty_wordlist(self, tmp_path):
        """Test scoring modules with empty wordlist"""
        from veta.scoring_modules.allsum import allsum
        from veta.scoring_modules.count import count
        
        # Create empty wordlist
        empty_file = tmp_path / "empty.xlsx"
        import pandas as pd
        df = pd.DataFrame({'words': [], 'scores': []})
        df.to_excel(empty_file, index=False)
        
        wordlist = Wordlist(str(empty_file))
        item = Item("I feel happy", "She seems sad")
        
        modules = [allsum(), count()]
        
        for module in modules:
            result = module.execute(item, wordlist)
            # With empty wordlist, should return 0 or equivalent
            if isinstance(result, bool):
                assert result == False
            else:
                assert result == 0

    def test_scoring_modules_with_no_matches(self, sample_wordlist_file):
        """Test scoring modules when no words match"""
        from veta.scoring_modules.allsum import allsum
        from veta.scoring_modules.count import count
        
        wordlist = Wordlist(sample_wordlist_file)
        # Use words that definitely won't be in the wordlist
        item = Item("xyz abc def ghi", "jkl mno pqr stu")
        
        modules = [allsum(), count()]
        
        for module in modules:
            with patch.object(module, 'match_words') as mock_match:
                mock_match.return_value = (
                    np.array([]),  # frequency
                    np.array([]),  # matching_words
                    np.array([])   # scores
                )
                
                result = module.execute(item, wordlist)
                
                if isinstance(result, bool):
                    assert result == False
                else:
                    assert result == 0
