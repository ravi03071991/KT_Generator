import os
import re

from llama_index import ListIndex
from llama_index import ServiceContext
from llama_index.llms import OpenAI
from llama_index.llms.palm import PaLM
from llama_index.response_synthesizers import get_response_synthesizer
from llama_index.schema import NodeRelationship
from llama_index.schema import RelatedNodeInfo
from llama_index.schema import TextNode


class ServiceConfiguration:
    def __init__(self, model_name="gpt-4"):
        # self.llm = PaLM(api_key=api_key)
        self.llm = OpenAI(model=model_name, temperature=0, max_tokens=512)

    def get_service_context(self):
        return ServiceContext.from_defaults(llm=self.llm)


class TextNodeManager:
    @staticmethod
    def get_nodes(texts):
        nodes = [TextNode(text=text, id_=str(idx)) for idx, text in enumerate(texts, start=1)]
        TextNodeManager._set_relationships(nodes)
        return nodes

    @staticmethod
    def _set_relationships(nodes):
        for idx, node in enumerate(nodes):
            if idx > 0:
                node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                    node_id=nodes[idx - 1].node_id
                )
            if idx < len(nodes) - 1:
                node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                    node_id=nodes[idx + 1].node_id
                )

        return nodes


class ResponseParser:
    PATTERN = r"Response \d+: (.*?)(?:\n---------------------|$)"

    @staticmethod
    def parse(response):
        return [resp.strip() for resp in re.findall(ResponseParser.PATTERN, response, re.DOTALL)]


class PromptManager:
    def __init__(self):
        self.short_line_description_prompt = (
            "Give a simple one-line description of what the code does?"
        )
        self.explanation_prompt = (
            "Give an explanation in 40 words maximum for the given code base. "
            "Don't include any code in your explanation. If the code is about import statements, "
            "give an overall explanation for import statements."
        )
        self.summary_prompt = "Give short summary for given codebase."

    def get_short_summaries_prompt(self):
        return self.short_line_description_prompt

    def get_explanation_prompt(self):
        return self.explanation_prompt

    def get_summary_prompt(self):
        return self.summary_prompt


class QueryHandler:
    def __init__(self, nodes, service_context):
        self.index = ListIndex(nodes, service_context=service_context)

        self.prompt_manager = PromptManager()

    def get_response(self, prompt="short_summaries"):
        query = ""
        response_mode = ""
        if prompt == "short_summaries":
            query = self.prompt_manager.get_short_summaries_prompt()
            response_mode = "accumulate"
        elif prompt == "explaination":
            query = self.prompt_manager.get_explanation_prompt()
            response_mode = "accumulate"
        elif prompt == "summary":
            query = self.prompt_manager.get_summary_prompt()
            response_mode = "tree_summarize"

        response_synthesizer = get_response_synthesizer(response_mode=response_mode)
        query_engine = self.index.as_query_engine(response_synthesizer=response_synthesizer)
        return query_engine.query(query)

    @staticmethod
    def modify_texts(original_texts, short_summaries):
        new_texts = [original_texts[0]]
        for i in range(1, len(original_texts)):
            new_text = f"The previous code has the following explanation: \n {short_summaries[i-1]}. \n Use this explanation only if required to explain the following code. \n {original_texts[i]}"
            new_texts.append(new_text)
        return new_texts
