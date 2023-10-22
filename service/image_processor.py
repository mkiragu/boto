import tempfile
from mindee import Client
from fastapi import UploadFile
from mindee.documents import TypeReceiptV5

import os
from dotenv import load_dotenv
load_dotenv()
mindee_api_key = os.getenv("MINDEE_API_KEY")

async def process_image(image: UploadFile):
	try:
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