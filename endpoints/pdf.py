from flask import Flask, send_file
from flask import request
from flask import g
from flask_restx import Namespace
from flask_restx import Resource as _Resource
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from models import StudentProfile
from models import StudentPersonalData
from models import Program
from datetime import datetime
from extensions.pdfgen.pdf_generator import generate_thank_you_letter
from extensions.pdfgen.pdf_generator import generate_acceptance_letter_and_contract
from extensions.pdfgen.pdf_generator import generate_invoice
from extensions.pdfgen.pdf_generator import generate_invitation
from extensions.pdfgen.pdf_generator import generate_placement

api = Namespace("pdf", description="")


@api.route("/<string:student_id>")
class PDFController(_Resource):
    def get(self, student_id):

        try:
            method = request.args.get("method")
            student_profile = StudentProfile.objects.get(id=student_id).to_json()
            student_personal_data = StudentPersonalData.objects.get(student_profile=student_profile['id']).to_json()
            programme = Program.objects.get(id=student_profile.get('program')).to_json()
            name = student_profile.get("first_name", "")
            address = student_personal_data.get("address")

            student_personal_data['parentsname'] = ""
            if "father" in student_personal_data:
                student_personal_data['parentsname'] += f'Mr {student_personal_data.get("father", {}).get("first_name", "")}'

            if "mother" in student_personal_data:
                student_personal_data['parentsname'] += f', Mrs {student_personal_data.get("mother", {}).get("first_name", "")}'

            elif "mother" in student_personal_data:
                student_personal_data['parentsname'] =+ f'Mrs {student_personal_data.get("mother", {}).get("first_name", "")}'

            student_personal_data.update({
                "name": f'{student_profile.get("first_name", "")} {student_profile.get("last_name", "")}',
                "address": f'{address.get("line_1", "")}, {address.get("city", "")}, {address.get("country", "")}',
                "first_name": student_profile.get("first_name", "")     
            })

            programme.update({
                "code": programme.get("code", ""),
                "country": programme.get("country", ""),
                "description": programme.get("description", ""),
                "price": programme.get("price", 0),
            })
        except Exception as e:
            pass
            
        if method == "generate_thank_you_letter": 
            generate_thank_you_letter(student_id, student_personal_data, programme)

        elif method == "generate_acceptance_letter_and_contract": 
            generate_acceptance_letter_and_contract(student_id, student_personal_data, programme)
        
        elif method == "generate_invoice": 
            generate_invoice(student_id, student_personal_data, programme)
        
        elif method == "generate_invitation": 

            pds = {}
            pds["dates"] = "dates"
            pds["name"] = "name"
            pds["address"] = "address"
            pds["contact_number"] = "contact number"
            pds["name"] = "name"
            pds["arrival_time"] = "arrival time"
            pds["name"] = "name"
            pds["end_time"] = "end time"            
            generate_invitation(student_id, student_personal_data, pds)
        
        elif method == "generate_placement": 
            generate_placement(student_id, student_personal_data, programme)

  
        return send_file("./extensions/pdfgen/tmp/pdf.pdf")
