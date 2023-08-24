import re
import logging
from textwrap import dedent
from lxml import etree
from typing import List
import html


class SlackUtil:
    def cleanup_message(message):
        return re.sub(r"<@\w+>", "", message).strip()

    def get_thread_or_event_ts(payload):
        if "thread_ts" in payload["event"]:
            return payload["event"]["thread_ts"]
        else:
            return payload["event"]["ts"]

    @staticmethod
    def extract_task_name(input_string: str):
        # Regular expression pattern to match the keyword
        pattern = r"TASK::(\w+)"

        # Search for the keyword in the input string
        match = re.search(pattern, input_string)

        if match:
            keyword = match.group(1)
            return keyword
        else:
            return None

    def extract_goal(input_string: str):
        # Split the text on "=>"
        parts = html.unescape(input_string).split("=>")

        if len(parts) > 1:
            # The second part of the split will be the desired goal
            goal = parts[1].strip()
            return goal
        else:
            return ""

    def summarize_history(history, show_items):
        logging.info(f"History size is {len(history)}")
        summary = []

        for message in history:
            role = message["role"]
            content = message["content"]

            # Split the content into lines
            lines = content.splitlines()

            # Take the first 3 lines
            first_3_lines = lines[:3]

            # Join the first 3 lines back into a string
            truncated_content = dedent("\n".join(first_3_lines)).strip()
            # Append to summary list
            summary.append(f"*{role}* => {truncated_content}")

        if show_items:
            logging.info("\n".join(summary))

        return "\n".join(summary)

    @staticmethod
    def _validate_markup(root: etree._Element) -> None:
        if root.tag != "questions":
            raise ValueError("Root element must be <questions>")
        expected_tags = ["question"]
        for child in root:
            if child.tag not in expected_tags:
                raise ValueError(f"Unexpected tag <{child.tag}> in <questions   >")

    @staticmethod
    def extract_questions(root: etree._Element) -> List[str]:
        questions = []
        for child in root:
            questions.append(child.text)
        return questions

    def parse_and_validate(xml_string: str) -> etree._Element:
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml_string, parser=parser)
            SlackUtil._validate_markup(root)
            return root
        except etree.XMLSyntaxError:
            raise ValueError("Invalid XML markup")
