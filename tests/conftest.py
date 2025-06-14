import pytest
import numpy as np
import pandas as pd
import tempfile
import os
from veta.wordlist import Wordlist
from veta.item import Item
from veta.respondent import Respondent
from veta.survey import Survey


@pytest.fixture
def sample_wordlist_data():
    """Sample wordlist data for testing"""
    return {
        'words': ['happy', 'sad', 'angry', 'joyful', 'depressed'],
        'scores': [4, 2, 1, 5, 1],
        'subclasses': [1, 1, 2, 1, 1]
    }


@pytest.fixture
def sample_wordlist_file(sample_wordlist_data, tmp_path):
    """Create a temporary wordlist Excel file"""
    file_path = tmp_path / "test_wordlist.xlsx"
    df = pd.DataFrame({
        'words': sample_wordlist_data['words'],
        'scores': sample_wordlist_data['scores'],
        'subclasses': sample_wordlist_data['subclasses']
    })
    df.to_excel(file_path, index=False)
    return str(file_path)


@pytest.fixture
def sample_wordlist_txt_file(sample_wordlist_data, tmp_path):
    """Create a temporary wordlist text file"""
    file_path = tmp_path / "test_wordlist.txt"
    with open(file_path, 'w') as f:
        # Add header lines as expected by loadFromTxt
        f.write("Test wordlist, created for testing\n")
        f.write("File to be used for testing LEAS scoring\n")
        # Write words and scores on separate lines as expected
        for word, score in zip(sample_wordlist_data['words'], sample_wordlist_data['scores']):
            f.write(f"{word}\n")
            f.write(f"{score}\n")
    return str(file_path)


@pytest.fixture
def wordlist_instance(sample_wordlist_file):
    """Create a Wordlist instance for testing"""
    return Wordlist(sample_wordlist_file)


@pytest.fixture
def sample_item():
    """Create a sample Item for testing"""
    return Item("I feel happy today", "She seems sad")


@pytest.fixture
def sample_respondent():
    """Create a sample Respondent for testing"""
    return Respondent(userid="test_user_001")


@pytest.fixture
def sample_survey():
    """Create a sample Survey for testing"""
    return Survey()


@pytest.fixture
def sample_survey_data():
    """Sample survey data matrix"""
    return np.array([
        ['ID', 'Self', 'Other', 'Score1', 'Score2'],
        ['user1', 'I feel happy', 'She is sad', '', ''],
        ['user1', 'I am excited', 'He is angry', '', ''],
        [np.nan, '', '', 8, 3],  # Totals row
        ['user2', 'I feel angry', 'She is joyful', '', ''],
        ['user2', 'I am depressed', 'He is happy', '', ''],
        [np.nan, '', '', 4, 9]   # Totals row
    ])


@pytest.fixture
def mock_spacy_doc():
    """Mock spacy document for testing"""
    class MockToken:
        def __init__(self, text, dep_, head_text):
            self.text = text
            self.dep_ = dep_
            self.head = MockToken(head_text, "", "") if head_text else None
    
    class MockDoc:
        def __init__(self, tokens):
            self.tokens = tokens
        
        def __iter__(self):
            return iter(self.tokens)
    
    return MockDoc([
        MockToken("I", "nsubj", "feel"),
        MockToken("feel", "ROOT", ""),
        MockToken("happy", "acomp", "feel"),
        MockToken("she", "nsubj", "seems"),
        MockToken("seems", "ROOT", ""),
        MockToken("sad", "acomp", "seems")
    ])
