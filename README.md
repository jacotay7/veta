# veta
A text-based emotion assessment tool called VETA (Verbal Emotion in Text Assessment). VETA was written to electronically score LEAS (Levels of Emotional Awareness Scale) surveys.

# Requirements

To use veta, you will need to install Python 3 and the Package Installer for Python (PiP).

# Installation

Clone the repository, navigate to the veta folder on your computer (the folder should contan the setup.py file) and run:

```
pip install .
```

# Vader

veta implements a scoring module that utilizes the python package for the vader sentiment analysis tool: https://github.com/cjhutto/vaderSentiment/tree/master.
This tool does support non-English text, but it will translate the text using the using **MY MEMORY NET http://mymemory.translated.net API which requires an active internet connection**. Users analyzing sensitive text should be aware of this before using the vader scoring module on non-English text.