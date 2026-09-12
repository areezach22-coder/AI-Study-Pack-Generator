ASSESSMENT_SYSTEM = """You are a strict university assessment generator.

Your task is to generate a study assessment in EXACTLY the JSON structure requested by the user.

You MUST produce syntactically valid JSON that can be parsed directly using Python json.loads().

Never output Markdown.
Never output ```json.
Never add comments.
Never add explanations outside the JSON object.
Never duplicate any JSON key.
Never add any extra key.
"""

ASSESSMENT_PROMPT = """
Create assessments from the learning plan and generated content.

LEARNING PLAN:
{planning}

GENERATED CONTENT:
{content}

STUDENT LEVEL:
{level}

REQUIRED COUNTS:

* Flashcards: exactly {flashcard_count}
* MCQs: exactly {mcq_count}
* Short-answer questions: exactly 5

IMPORTANT JSON RULES:

1. Return ONLY one valid JSON object.

2. The JSON must contain EXACTLY these three top-level keys:

   * "flashcards"
   * "mcqs"
   * "short_questions"

3. Each flashcard must contain EXACTLY two keys:

   * "question"
   * "answer"

4. Each MCQ must contain EXACTLY four keys:

   * "question"
   * "options"
   * "correct_answer"
   * "explanation"

5. Each MCQ "options" array must contain EXACTLY four unique options.

6. "correct_answer" must be exactly one of:
   "A", "B", "C", or "D"

7. Never repeat "answer", "question", or any other key inside an object.

8. Never put an "answer" key outside its flashcard object.

9. Do not create nested duplicate objects.

10. Do not add extra fields.

11. Generate exactly the requested number of flashcards and MCQs.

12. Generate exactly 5 short-answer questions.

13. All questions must be based on the supplied learning plan and generated content.

14. Do not invent unsupported facts.

15. Make MCQs unambiguous and academically meaningful.

16. Before returning the response, internally verify:

    * JSON brackets are correctly closed.
    * Every key appears only once within its object.
    * Every flashcard has exactly question + answer.
    * Every MCQ has exactly question + options + correct_answer + explanation.
    * Every MCQ has exactly four unique options.
    * The number of flashcards is exactly {flashcard_count}.
    * The number of MCQs is exactly {mcq_count}.
    * There are exactly 5 short questions.

RETURN THIS EXACT STRUCTURE:

{{
"flashcards": [
{{
"question": "Question 1",
"answer": "Answer 1"
}}
],
"mcqs": [
{{
"question": "Question 1",
"options": [
"Option A",
"Option B",
"Option C",
"Option D"
],
"correct_answer": "A",
"explanation": "Explanation"
}}
],
"short_questions": [
"Question 1",
"Question 2",
"Question 3",
"Question 4",
"Question 5"
]
}}

IMPORTANT:
The example above shows the required structure only.
Do NOT copy the example questions.
Generate the actual questions from the supplied content.

Return ONLY valid JSON.
"""


