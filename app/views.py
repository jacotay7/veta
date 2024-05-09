from app import app
from flask import request, render_template, jsonify, send_from_directory
import re
from veta.item import Item
from veta.respondent import Respondent
from veta.survey import Survey
from veta.scoring_modules.allsum import allsum
from veta.scoring_modules.highestN import highestN
from veta.scoring_modules._3345plus import _3345plus
from veta.scoring_modules._334 import _334
from veta.scoring_modules.mlr import mlr

import openpyxl
from openpyxl.styles import Font
import pandas as pd
import os


all_answers = []
current_user=None
workbook = openpyxl.Workbook()
header_row = ["Person", "Self", "Other"]
sheet = workbook.active
sheet.append(header_row)
header_cell = sheet[1]
for cell in header_cell:
    cell.font = Font(bold=True)

person=1
@app.route('/answers', methods=['POST'])
def get_wordlist():
    try:
        global person, workbook, sheet, current_user
        decoded_data = request.json
        answer_data = decoded_data['answersData']
        current_user = decoded_data['user']

        if answer_data not in all_answers:
            all_answers.append(answer_data)
            answer_with_counter = [person] + answer_data  # Add counter to the beginning of the answer_data list
            sheet.append(answer_with_counter)
            person = 1

        workbook.save(f"{current_user}.xlsx")
        return jsonify({'Success': True, 'Data': answer_data})
    except Exception as e:
        return jsonify({'Success': False, 'message':str(e)})
    
@app.route('/execute-script', methods=['POST'])
def generateReport():
    print('123')
    global current_user
    try:
        decoded_data = request.json
        current_user = decoded_data['userReportName']
        example_survey = Survey("output.xlsx")
        example_survey.from_file(f'{current_user}.xlsx')
        modules = [allsum(), highestN(4), _334(), _3345plus(), mlr()]
        example_survey.score(*modules)

        example_survey.compute_summary()

        example_survey.save(f'{current_user}.xlsx')
        return jsonify({'success': True, 'message': 'Report generated successfully'}), 200
    except Exception as e:
        print(f"Error in Generating Report: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/download-report')
def downloadReport():
    try:
        global current_user
        if current_user is None:
            return jsonify({'error': 'No report file available to download'}), 404
        output_folder = os.path.join(os.getcwd(), '')
        file_to_download = f'{current_user}.xlsx'
        return send_from_directory(directory=output_folder,path=file_to_download, as_attachment=True)
    except Exception as e:
        print(f"Error in downloadReport: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500