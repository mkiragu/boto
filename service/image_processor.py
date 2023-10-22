import tempfile
from mindee import Client
from fastapi import UploadFile
from mindee.documents import TypeReceiptV5
import requests
import os
from dotenv import load_dotenv

async def process_mindee_image(image: UploadFile):
	try:
		load_dotenv()
		mindee_api_key = os.getenv("MINDEE_API_KEY")

		# Read the image data from the UploadFile object
		image_data = await image.read()

		# Create a temporary file and write the image data to it
		with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
			temp_file.write(image_data)

		# Create a Mindee document from the temporary file
		mindee_client = Client(api_key=mindee_api_key)
		input_doc = mindee_client.doc_from_path(temp_file.name)
		
		# Replace "TypeReceiptV5" with the appropriate parsing type
		result = input_doc.parse(TypeReceiptV5)

		# Process the parsed data or return it as needed
		return {"parsed_data": result.document}

	except Exception as e:
		return {"error": str(e)}
	
async def process_nanonets_image(image: UploadFile):
	try:
		load_dotenv()
		nanonets_api_key = os.getenv("NANONETS_API_KEY")
		nanonets_model_id = os.getenv("NANONETS_MODEL_ID")
		NANONETS_API_URL = f"https://app.nanonets.com/api/v2/OCR/Model/{nanonets_model_id}/LabelFile/?async=false"

		# Prepare the image file data to send to Nanonets
		files = {'file': (image.filename, image.file)}

		# Send a POST request to Nanonets with the image file
		response = requests.post(
			NANONETS_API_URL,
			auth=requests.auth.HTTPBasicAuth(nanonets_api_key, ''),
			files=files
		)

		# Process Nanonets' response
		nanonets_result = response.json()

		# You can return the JSON response from Nanonets to your client
		return nanonets_result

	except Exception as e:
		return {"error": str(e)}