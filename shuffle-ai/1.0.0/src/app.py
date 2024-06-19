import json
import PyPDF2
import tempfile
import requests
import pytesseract
from pdf2image import convert_from_path

from walkoff_app_sdk.app_base import AppBase

class Tools(AppBase):
    __version__ = "1.0.0"
    app_name = "Shuffle AI"  

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def autoformat_text(self, apikey, text, formatting="auto"):
        headers = {
            "Authorization": "Bearer %s" % apikey,
        }

        if not formatting:
            formatting = "auto"
    
        output_formatting= "Format the following data to be a good email that can be sent to customers. Don't make it too business sounding."
        if formatting != "auto":
            output_formatting = formatting
    
        ret = requests.post(
            "https://shuffler.io/api/v1/conversation", 
            json={
                "query": text, 
                "formatting": output_formatting,
                "output_format": "formatting"
            },
            headers=headers,
        )
    
        if ret.status_code != 200:
            print(ret.text)
            return {
                "success": False,
                "reason": "Status code for auto-formatter is not 200"
            }
    
        return ret.text

    def generate_report(self, apikey, input_data, report_title, report_name="generated_report.html"):
        headers = {
            "Authorization": "Bearer %s" % apikey,
        }

        if not report_name:
            report_name = "generated_report.html"

        if "." in report_name and not ".html" in report_name:
            report_name = report_name.split(".")[0]

        if not "html" in report_name:
            report_name = report_name + ".html"

        report_name = report_name.replace(" ", "_", -1)
        output_formatting= "Format the following text into an HTML report with relevant graphs and tables. Title of the report should be {report_title}."
        ret = requests.post(
            "https://shuffler.io/api/v1/conversation", 
            json={
                "query": text, 
                "formatting": output_formatting,
                "output_format": "formatting"
            },
            headers=headers,
        )
    
        if ret.status_code != 200:
            print(ret.text)
            return {
                "success": False,
                "reason": "Status code for auto-formatter is not 200"
            }

        # Make it into a shuffle file with self.set_files()
        new_file = {
            "name": report_name,
            "data": ret.text,
        }

        retdata = self.set_files([new_file])
        if retdata["success"]:
            return retdata

        return {
            "success": False,
            "reason": "Failed to upload file"
        }


    def extract_text_from_pdf(self, file_id):
        def extract_pdf_text(pdf_path):
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()

            return text

        def extract_text_from_images(images):
            text = ''
            for image in images:
                extracted_text = pytesseract.image_to_string(image, lang='eng')
                text += extracted_text
            return text

        def extract_text_from_pdf_with_images(pdf_path):
            images = convert_from_path(pdf_path)
            return extract_text_from_images(images)

        def export_text_to_json(image_text, extracted_text):
            data = {
                "success": True,
                'image_text': image_text,
                'extracted_text': extracted_text,
            }
            
            #with open(output_path, 'w+') as file:
            #    json.dump(data, file, indent=4)

            return data

        pdf_data = self.get_file(file_id)
        defaultdata = {
            "success": False,
            "file_id": file_id,
            "filename": pdf_data["filename"],
            "reason": "Something failed in reading and parsing the pdf. See error logs for more info",
        }

        # Make a tempfile for the file data from self.get_file
        # Make a tempfile with tempfile library
        with tempfile.NamedTemporaryFile() as temp:
            # Write the file data to the tempfile
            # Get the path to the tempfile
            temp.write(pdf_data["data"])
            pdf_path = temp.name

            # Extract text from the PDF
            extracted_text_from_pdf = extract_pdf_text(pdf_path)
            
            # Extract text from the PDF using images
            extracted_text_from_images = extract_text_from_pdf_with_images(pdf_path)
            
            # Combine the extracted text
            
            # Export combined text to JSON
            #output_path = pdf_path.split(".")[0] + ".json"
            exported_text = export_text_to_json(extracted_text_from_images, extracted_text_from_pdf)
            exported_text["file_id"] = file_id
            exported_text["filename"] = pdf_data["filename"]
            return exported_text

        return defaultdata

    def extract_text_from_image(self, file_id):
        # Check if it's a pdf
        # If it is, use extract_text_from_pdf
        # If it's not, use pytesseract
        if self.get_file(file_id)["name"].endswith(".pdf"):
            return self.extract_text_from_pdf(file_id)

        pdf_data = self.get_file(file_id)
        defaultdata = {
            "success": False,
            "file_id": file_id,
            "filename": pdf_data["filename"],
            "reason": "Something failed in reading and parsing the pdf. See error logs for more info",
        }

        with tempfile.NamedTemporaryFile() as temp:
            # Load temp as Image
            # Write the file data to the tempfile
            # Get the path to the tempfile
            temp.write(pdf_data["data"])
            pdf_path = temp.name

            image = Image.open(temp.name)
            image = image.resize((500,300))
            custom_config = r'-l eng --oem 3 --psm 6'
            text = pytesseract.image_to_string(image,config=custom_config)

            data = {
                "success": True,
                'extracted_text': text,
            }

            return data
        
        return defaultdata

    def transcribe_audio(self, file_id):
        return {
            "success": False,
            "reason": "Not implemented yet"
        }

    def find_image_objects(self, file_id):
        return {
            "success": False,
            "reason": "Not implemented yet"
        }

    def gpt(self, input_text):
        return {
            "success": False,
            "reason": "Not implemented yet"
        }

    def run_schemaless(self, category, action, app_name="", fields=""):
        self.logger.info("[DEBUG] Running schemaless action with category '%s' and action label '%s'" % (category, action))

        """
		action := shuffle.CategoryAction{ 
			Label: step.Name,
			Category: step.Category,
			AppName: step.AppName,
			Fields: step.Fields,

			Environment: step.Environment,

			SkipWorkflow: true,
		}
        """

        data = {
            "label": action,
            "category": category,

            "app_name": "",
            "fields": [],

            "skip_workflow": True,
        }

        if app_name:
            data["app_name"] = app_name

        self.logger.info(f"\n\nFIELDS MAPPED\n\n: {fields}")

        if fields:
            if isinstance(fields, list):
                data["fields"] = fields

            elif isinstance(fields, dict):
                for key, value in fields.items(): 
                    data["fields"].append({
                        "key": key,
                        "value": str(value),
                    })

            else:
                fields = str(fields).strip()
                if not fields.startswith("{") and not fields.startswith("["):
                    fields = json.dumps({
                        "data": fields,
                    })

                try:
                    loadedfields = json.loads(fields)
                    for key, value in loadedfields.items(): 
                        data["fields"].append({
                            "key": key,
                            "value": value,
                        })

                except Exception as e:
                    self.logger.info("[ERROR] Failed to load fields as JSON: %s" % e)
                    return json.dumps({
                        "success": False,
                        "reason": "Ensure 'Fields' are valid JSON",
                        "details": "%s" % e,
                    })


        baseurl = "%s/api/v1/apps/categories/run" % self.base_url
        baseurl += "?execution_id=%s&authorization=%s" % (self.current_execution_id, self.authorization) 

        self.logger.info("[DEBUG] Running schemaless action with URL '%s', category %s and action label %s" % (baseurl, category, action))

        headers = {}
        request = requests.post(
            baseurl,
            json=data,
            headers=headers,
        )

        try: 
            if "parameters" in self.action:
                response_headers = request.headers
                for key, value in response_headers.items():
                    if not str(key).lower().endswith("-url"):
                        continue

                    self.action["parameters"].append({
                        "name": key,
                        "value": value,
                    })

                    #self.logger.info("[DEBUG] Response header: %s: %s" % (key, value))
        except Exception as e:
            self.logger.info("[ERROR] Failed to get response headers (category action url debug mapping): %s" % e)

        try: 
            return request.json()
        except:
            return request.text

if __name__ == "__main__":
    Tools.run()
