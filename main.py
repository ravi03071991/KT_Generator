# %%
from CarbonSnippets import *
from CodeParser import *
from CreateVideo import *
from DIDVideoGenerator import *
from ResponseGenerator import *

save_path = "./kt_gen"
avatar_image_url = "<IMAGE-URL>"
test_code = "<FILE-NAME>"
palm_api_key = "<PALM_API_KEY>"
# Split the code using parser
with open(test_code, "r") as f:
    source = f.read()

codeparser = code_parser()
extracted_elements = codeparser.extract_elements(source)

# %%
# Generate carbon snippets
generate_carbon_snippets(extracted_elements, save_path)

# %%
# Generate Explainations and Summaries
service_context_manager = ServiceConfiguration(palm_api_key)
service_context = service_context_manager.get_service_context()
text_node_manager = TextNodeManager()
response_parse_manager = ResponseParser()

# Generate short summary
nodes = text_node_manager.get_nodes(extracted_elements)

query_handler = QueryHandler(nodes, service_context)
short_summary_response = query_handler.get_response("short_summaries")
short_summaries = response_parse_manager.parse(short_summary_response.response)
summary = query_handler.get_response("summary").response

# Generate explainations
new_texts = query_handler.modify_texts(extracted_elements, short_summaries)
new_nodes = text_node_manager.get_nodes(new_texts)

query_handler = QueryHandler(new_nodes, service_context)
explaination_response = query_handler.get_response("explaination")
explaination_summaries = response_parse_manager.parse(explaination_response.response)

# %%
# Generate video
video_processor = DIDVideoGeneration(source_url=avatar_image_url)

video_processor.process_chunk(summary, "summaries", save_path)
for index, chunk in enumerate(explaination_summaries):
    video_processor.process_chunk(chunk, index, save_path)

# %%
# Stitch videos and images together
stitch_video(save_path, len(extracted_elements), len(extracted_elements))
print("Video and image stitching with circular mask complete.")
