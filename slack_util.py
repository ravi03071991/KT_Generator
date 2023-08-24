from assistant.models import Task, Question, Consideration
from assistant.slack.slack_bot import SlackBot
from assistant.core.open_ai_client import OpenAIClient
from assistant.core.prompt import Prompts
from assistant.slack.slack_util import SlackUtil

BACKGROUND_JOB_CONSIDERATIONS = [
    Consideration(
        category="background job",
        text="""
        Good specifications must have clarity on considerations like:
        
            1. exact schedule when the job will be executed; without a story can't be completed
            2. who and where will manage the configuration for scheduling. will it be devs managing these OR a system admin?
                  
        Good specification must also have clarity on negative use-cases like:
                  
            1. if a job fails, how many times should it be retried?
            2. what's the gap between two retries?
            3. if job fails on the last retry, who should be notified?
    """,
    ),
    Consideration(
        category="email notification",
        text="""
        Good specifications must have clarity on considerations like:
        
            1. exact template for the email; without that a story can't be completed
            2. what's the email address on which such emails must be sent
            3. can the user unsubscribe to these emails?
                  
        Good specification must also have clarity on negative use-cases like:
                  
            1. if an email bounces, do we need to address it specifically?
    """,
    ),
    Consideration(
        category="content summarization",
        text="""
        Good specifications must have clarity on considerations like:
                  
            1. what information should be included in the summary?
            2. what are the sources of each of that information?
    """,
    ),
]

# pylint: disable=too-few-public-methods
class InteractiveSpecificationTask(Task):
    class Meta:
        proxy = True

    @classmethod
    def get_task_type(cls):
        return "InteractiveSpecification"

    def add_considerations(self):
        for consideration in BACKGROUND_JOB_CONSIDERATIONS:
            consideration.task = self
            consideration.save()

    def considerations(self):
        considerations = Consideration.objects.filter(task=self)
        return list(considerations)

    def set_consideration_at_hand(self, consideration):
        if consideration:
            self.extra_data["consideration_at_hand"] = str(consideration.id)
        else:
            self.extra_data["consideration_at_hand"] = None
        self.save()

    def get_consideration_at_hand(self):
        consideration_id = self.extra_data.get("consideration_at_hand")
        if consideration_id is not None:
            return Consideration.objects.get(id=consideration_id)
        return None

    def set_question_at_hand(self, question):
        if question:
            self.extra_data["question_at_hand"] = str(question.id)
        else:
            self.extra_data["question_at_hand"] = None
        self.save()

    def get_question_at_hand(self):
        question_id = self.extra_data.get("question_at_hand")
        if question_id is not None:
            return Question.objects.get(id=question_id)
        return None

    def get_unfulfilled_consideration(self):
        for consideration in self.considerations():
            if not consideration.is_fulfilled():
                return consideration
        return None

    def kick_off(self, bot: SlackBot):
        self.add_considerations()
        open_ai_client = OpenAIClient(bot.history)
        for consideration in self.considerations():
            prompt = Prompts.QUESTIONS_FOR_A_CONSIDERATION.instructions.format(
                goal=self.goal, category=consideration.category, considerations=consideration.text
            )
            response = open_ai_client.create_chat(prompt)
            root = SlackUtil.parse_and_validate(response)
            questions = SlackUtil.extract_questions(root)
            for question_text in questions:
                consideration.add_question(question_text)

            if self.extra_data.get("question_at_hand") is None:
                self.set_consideration_at_hand(consideration)
                self.set_question_at_hand(consideration.questions()[0])

        bot.post_slack_message(self.get_question_at_hand().question_text)
        bot.store_history(open_ai_client.get_history())

    def handle_user_response(self, bot: SlackBot, user_input: str):
        consideration_at_hand = self.get_consideration_at_hand()
        question_at_hand = self.get_question_at_hand()
        if consideration_at_hand is None or question_at_hand is None:
            raise ValueError("not sure why this method got called if no question is at hand")

        consideration_at_hand.answer_question(question_at_hand, user_input)

        if consideration_at_hand.is_fulfilled:
            # iterate over other questions to check if there is another unfulfilled question
            unfulfilled_consideration = Consideration.get_unfulfilled_consideration()
            if unfulfilled_consideration is None:
                self.generate_story(bot)
                self.set_question_at_hand(None)
                self.set_consideration_at_hand(None)
            else:
                question_at_hand = unfulfilled_consideration.get_unanswered_question()
                self.set_consideration_at_hand(unfulfilled_consideration)
                self.set_question_at_hand(question_at_hand)
                bot.post_slack_message(question_at_hand.question_text)
        else:
            self.set_question_at_hand(consideration_at_hand.get_unanswered_question())
            bot.post_slack_message(self.get_question_at_hand().question_text)

    def generate_story(self, bot: SlackBot):
        open_ai_client = OpenAIClient(bot.history)
        # iterate over considerations and underlying questions to build an xml of question and corresponding answers
        xml = ""
        for consideration in self.considerations():
            xml += f"<{consideration.category}>"
            for question in consideration.questions():
                xml += f"""
                <question-answer>
                    <question>{question.question_text}</question>
                    <answer>{question.question_text}</answer>
                </question-answer>
                """
            xml += f"</{consideration.category}>"

        response = open_ai_client.create_chat(Prompts.PM_STORY_GENERATION.instructions.format(question_answers=xml))
        bot.post_slack_message(response)
