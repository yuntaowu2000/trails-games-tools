from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
# If you are using a Jupyter notebook, uncomment the following line.
# %matplotlib inline
import sys
from google_trans_new import google_translator

endpoint = "https://sennokisekiocr.cognitiveservices.azure.com/"
subscription_key = "21fa2e7ef7e14e708b40d33df8c09069"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

headers = {'Ocp-Apim-Subscription-Key': subscription_key}

params = {'language': 'ja', 'detectOrientation': 'true'}

image_path = sys.argv[1]
# Read the image into a byte array
image_data = open(image_path, "rb")
# Set Content-Type to octet-stream
# put the byte array into your post request

ocr_result_local = computervision_client.recognize_printed_text_in_stream(image_data)

# Extract the word bounding boxes and text.
line_infos = [region.lines for region in ocr_result_local.regions]
word_infos=""
for line in line_infos:
    for word_metadata in line:
        for word_info in word_metadata.words:
            word_infos += word_info.text

with open("original.txt","a+",encoding='utf-8') as f1:
    f1.write(word_infos)
    f1.write('\n\n')

translator = google_translator()
translated = translator.translate(word_infos, lang_tgt= 'zh-cn')

with open("translated.txt", "a+", encoding='utf-8') as f:
    f.write(translated)
    f.write('\n\n')
    

