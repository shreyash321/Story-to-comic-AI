import requests
import io
import re
from PIL import Image
from PIL import Image, ImageDraw, ImageFont
import textwrap
import google.generativeai as palm
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": "Bearer your_hugging_face_api"}
def lang_model(user_text):
  messages=['hello create a interesting comic story in 100 words']
  palm.configure(api_key="your_palm_api_key")
  defaults = {
    'model': 'models/chat-bison-001',
    'temperature': 0.9,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
  }
  context = "Be a comic story writer for the audience of age between 17 to 30 and generate interesting story for it "
  examples = [
    [  "hello can you generate a story based on a hospital lady worker",
        "once was a lady nurse in a children's hospital "
    ],
    [
        'can you make it interesting',
        'the lady then helped out by giving some amount of her salary for the operation of the poor boy and then also helped in his further education'
    ]
  ]
  def lang(question):
    messages.append(question)
    response = palm.chat(
        **defaults,
        context=context,
        examples=examples,
        messages=messages)
    g=response.last # Response of the AI to your most recent request
    def replace(string, replacements):
      new_string = ""
      for character in string:
        if character in replacements:
          new_string += replacements[character]
        else:
          new_string += character
      return new_string
    string=g
    replacements = {"\n" : " ", "\r" : " ", "\s" : " ","\t":" "}
    new_string = replace(string,replacements)
    messages.append(new_string)
    return new_string
  return lang(f"create a python list for generating interesting captions for a comic that - {user_text}, give only single caption for each page and give a python list as output ")
para=lang_model(input())
def find_captions(paragraph):
# Find the start and end indices of the list content
    start_index = para.find(" [")
    end_index = para.find("]", start_index) + 3
    # Extract the list content
    list_content = para[start_index:end_index]
    # Clean up the list content (remove leading/trailing whitespace and line breaks)
    list_content = list_content.strip()
    # Split the list content into individual captions
    captions = [caption.strip() for caption in list_content.split(",")]
    page=[]
    # Print the captions list
    for caption in captions:
      page.append(caption)
    return page
pages=find_captions(para)
pages[0]=pages[0].replace('[','')
for i in range (0,len(pages)):
  def text_to_image(text):
    def query(payload):
      response = requests.post(API_URL, headers=headers, json=payload)
      return response.content
    image_bytes = query({
      "inputs": f"a single and highly detailed 4k manga realistic comic style color image of {text}, detailed eyes and face, portrait A4 page for a comic",
    })
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)

    # Define the text to be drawn
    text = pages[i]

    # Define the font properties
    font_path = '/content/ComicNeue-BoldItalic.ttf'  # Replace with the path to your custom font file (.ttf)
    font_size = 36
    font_color = (0, 0, 0)

    # Load the custom font
    font = ImageFont.truetype(font_path, font_size)

    # Wrap the text to fit within the specified width
    wrapped_text = textwrap.fill(text, width=40)  # Adjust the width as needed

    # Define the position to draw the text (top left corner)
    x = 30
    y = 40

    # Draw the wrapped text on the image
    draw.text((x, y), wrapped_text, fill=font_color, font=font)

    # Save the image with the text
    output_image_path = f'output_image{i}.jpg'
    image.save(output_image_path)
    # Close the image
    image.close()
    return image
  text_to_image(pages[i])
# You can access the image with PIL.Image for example