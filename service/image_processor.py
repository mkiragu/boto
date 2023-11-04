import tempfile
from mindee import Client
from fastapi import UploadFile
from mindee.documents import TypeReceiptV5
import requests
import os
import boto3
from dotenv import load_dotenv

async def process_aws_image(image: UploadFile):

	load_dotenv()
	aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
	aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY_ID")
	client = boto3.client('textract', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)

	# Read the data from the UploadFile
	data = await image.read()
    
	response = client.analyze_expense(Document={'Bytes': data})

	summary_fields_value_pairs = {}

	# Iterate through the data to extract LabelDetection and ValueDetection
	for summary_field in response["ExpenseDocuments"][0]["SummaryFields"]:
		label_detection = summary_field.get("Type", {}).get("Text")
		value_detection = summary_field.get("ValueDetection", {}).get("Text")
		if label_detection and value_detection:
			summary_fields_value_pairs[label_detection] = value_detection

	print(summary_fields_value_pairs)

	# Create a dictionary to store LineItems and their Type-ValueDetection pairs
	line_item_pairs = []

	# Iterate through the data to extract Type and ValueDetection
	for line_item_group in response["ExpenseDocuments"][0]["LineItemGroups"]:
		
		# Iterate through LineItems
		for line_item in line_item_group["LineItems"]:
			line_item_expense_fields = line_item.get("LineItemExpenseFields", [])
			
			# Initialize a dictionary to store Type-ValueDetection pairs for this LineItem
			line_item_data = {}
			
			# Iterate through LineItemExpenseFields
			for field in line_item_expense_fields:
				field_type = field["Type"]["Text"]
				value_detection = field["ValueDetection"]["Text"]
				
				# Add the Type-ValueDetection pair to the LineItem dictionary
				line_item_data[field_type] = value_detection
			
			# Append the LineItem dictionary to the list for this LineItemGroup
			line_item_pairs.append(line_item_data)

	summary_fields_value_pairs["line_items"] = line_item_pairs

	return summary_fields_value_pairs

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
	