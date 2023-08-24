import os
from enum import Enum
from loguru import logger
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "OPENAI_API_KEY is not set!"
openai.api_key = OPENAI_API_KEY


CLASS_EXPLAINATION_PROMPT = """
Following is most of the code & script you need to keep in mind to generate the script:

<code>
{context_code}
</code>

<context>
This class is part of the larger codebase that provides interative agents that assists various roles in Software Delivery Life Cycles.
</context>

Please generate the script that provides a 100 words nontechnical very high level purpose of class `{class_name}`.

Rules:
1. Provide only the script in the output and no greetings/acknowledgement/etc.
2. Be professional, don't use too many analogies
3. Limit to 100 words max
"""

METHOD_EXPLAINATION_PROMPT = """
Following is most of the code you need to keep in mind to generate the script:

<code>
{context_code}
</code>

<context>
This class is part of the larger codebase that provides interative agents that assists various roles in Software Delivery Life Cycles.
</context>

Please generate the script that provides a nontechnical explanation for the method `{method_name}`.

Script should cover:
1. Brief summary of when one should use this method
2. Brief summary of primary building blogs used in the method
3. How these building blocks come together to achieve the output
4. Any special case that the listener should notice while understanding the  control/flow
5. Do not talk about any validations, error management OR exceptions raised

Rules:
1. Provide only the script in the output and no greetings/acknowledgement/etc.
2. Be professional, don't use too many analogies
3. Limit to 300 words max
4. Ignore error management & validations
"""

class OpenAIClient:
    def __init__(self, provided_history=None):
        self.history = provided_history
        if self.history is None or len(self.history) == 0:
            self.history = []
            logger.info("No history provided. Setting up system...")
            self.setup_system()

    def setup_system(self):
        self.history.append(
            {
                "role": "system",
                "content": f"""
                You are an experienced Python developer who is asked to write a script that will be read 
                and recorded by a professional reader to record knowledge transfer videos. The code is 
                for the domain of getting AI agents to interact with humans to generate a User Story. You 
                are good at explaining code to non-technical people using language they will understand.
                """,
            }
        )

    def create_chat(self, message, temperature=0.8, presence_penalty=0, frequency_penalty=0):
        self.history.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model=os.environ.get("OPENAI_MODEL_ID"),
            messages=self.history,
            temperature=temperature,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )

        response_content = response.choices[0].message["content"].strip()
        self.history.append({"role": "assistant", "content": response_content})

        return response_content.replace("```\n", "```\n##### ")

    def get_history(self):
        return self.history
    
    def reset_history(self):
        self.history = []
        self.setup_system()
