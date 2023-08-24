# %%
from CarbonSnippets import *
from CodeParser import *
from CreateVideo import *
from DIDVideoGenerator import *
from ResponseGenerator import *
import ast
from open_ai_client import OpenAIClient, METHOD_EXPLAINATION_PROMPT, CLASS_EXPLAINATION_PROMPT

from loguru import logger

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

open_ai_client = OpenAIClient()

# UTIL Methods Start


def find_string_from_array(elements, pattern):
    for s in elements:
        if pattern in s:
            return s
    return None


def get_method_name(method_declaration):
    # Parse the method declaration using the ast module
    parsed_ast = ast.parse(method_declaration)

    # Find the first function definition node in the parsed AST
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.FunctionDef):
            return node.name

    return None
# UTIL Methods End


save_path = "./kt_gen3"
avatar_image_url = "https://gcdnb.pbrd.co/images/UaLr3QRi4IDq.png"
test_code = "slack_util.py"

logger.info("Starting the processing...")

# # Split the code using parser
with open(test_code, "r") as f:
    source = f.read()

codeparser = code_parser()
extracted_elements = codeparser.extract_elements(source)

logger.info("Code parsing completed...")

# iterate over extracted elements and print each element
class_element = find_string_from_array(
    extracted_elements, 'InteractiveSpecificationTask')
method_elements = []
method_elements.append(find_string_from_array(
    extracted_elements, 'def kick_off'))
method_elements.append(find_string_from_array(
    extracted_elements, 'def handle_user_response'))

# %%
# Generate carbon snippets
elements_for_images = [class_element]+method_elements
generate_carbon_snippets(elements_for_images, save_path)

video_scripts = []

# generate class script
class_prompt = CLASS_EXPLAINATION_PROMPT.format(
    context_code=source, class_name='InteractiveSpecificationTask')
class_script = open_ai_client.create_chat(class_prompt)
video_scripts.append(class_script)
logger.info(class_script)

# generate method scripts
for element in method_elements:
    open_ai_client.reset_history()
    method_name = get_method_name(element)
    logger.info(method_name)
    method_prompt = METHOD_EXPLAINATION_PROMPT.format(
        context_code=source, method_name=method_name)
    method_script = open_ai_client.create_chat(method_prompt)
    video_scripts.append(method_script)
    logger.info(method_script)

# %%
# Generate video
video_processor = DIDVideoGeneration(source_url=avatar_image_url)

# video_processor.process_chunk(summary, "summaries", save_path)
for index, chunk in enumerate(video_scripts):
    logger.info(f"Chunk {index} video generation started...")
    video_processor.process_chunk(chunk, index, save_path)
    logger.info(f"Chunk {index} video generation completed...")

# %%
# Stitch videos and images together
video_paths = [os.path.join(save_path, f"chunk_{i}.mp4") for i in range(
    len(extracted_elements))]
image_paths = [os.path.join(save_path, f"image_{i}.png") for i in range(
    len(extracted_elements))]
stitch_video(save_path, video_paths, image_paths)
