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
This tool does support non-English text, but it will translate the text using the using the Google Translate API. Users analyzing sensitive text should be aware of this before using the vader scoring module on non-English text.

## Citation

For feedback and feature requests contact me via e-mail at jacob.taylor@mail.utoronto.ca . Please cite us if you use this code in your analysis:

```
Herpertz J, Taylor J, Allen JJB, Herpertz S, Opel N, Richter M, Subic-Wrana C, Dieris-Hirche J and Lane RD (2023) Development and validation of a computer program for measuring emotional awareness in German—The geLEAS (German electronic Levels of Emotional Awareness Scale). Front. Psychiatry 14:1129755. doi: 10.3389/fpsyt.2023.1129755
```

### BibTex Entry:

```
@article{Herpertz2023,
  doi = {10.3389/fpsyt.2023.1129755},
  url = {https://doi.org/10.3389/fpsyt.2023.1129755},
  year = {2023},
  month = mar,
  publisher = {Frontiers Media {SA}},
  volume = {14},
  author = {Julian Herpertz and Jacob Taylor and John J. B. Allen and Stephan Herpertz and Nils Opel and Maike Richter and Claudia Subic-Wrana and Jan Dieris-Hirche and Richard D. Lane},
  title = {Development and validation of a computer program for measuring emotional awareness in German{\textemdash}The {geLEAS} (German electronic Levels of Emotional Awareness Scale)},
  journal = {Frontiers in Psychiatry}
}
```