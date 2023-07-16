from setuptools import setup

setup(
    name='veta',
    version='1.0.1',    
    description='A text-based emotion assessment tool to electronically score LEAS (Levels of Emotional Awareness Scale) surveys.',
    url='https://github.com/jacotay7/veta',
    author='Jacob Taylor',
    author_email='jacob.taylor@mail.utoronto.ca',
    license='MIT',
    packages=['veta',
              'veta.scoring_modules'],
    install_requires=['pandas',
                      'numpy',
                      'matplotlib',
                      'spacy',
                      'vaderSentiment',
                      'openpyxl',
                      'requests'                     
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Environment :: MacOS X',  
        'Operating System :: OS Independent',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)