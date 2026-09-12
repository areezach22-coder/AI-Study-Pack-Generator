PLANNING_SYSTEM = """You are an expert instructional designer. Create accurate, personalized learning plans."""

PLANNING_PROMPT = """
Create a personalized learning plan.

Topic: {topic}
Student level: {level}
Study-pack type: {pack_type}
Flashcards: {flashcard_count}
MCQs: {mcq_count}
Study material: {material}

Return ONLY valid JSON:
{{
  "topic": "final topic",
  "learning_goal": "main goal",
  "learning_objectives": ["objective 1", "objective 2", "objective 3", "objective 4"],
  "core_concepts": ["concept 1", "concept 2", "concept 3"],
  "difficulty": "appropriate difficulty",
  "content_strategy": "explanation strategy",
  "assessment_strategy": "assessment strategy",
  "common_misconceptions": ["misconception 1", "misconception 2"]
}}
Prioritize supplied material and do not invent unsupported facts.
"""

CONTENT_SYSTEM = """You are an expert university teacher. Generate accurate, clear, student-friendly learning content."""

CONTENT_PROMPT = """
Generate teaching content from this learning plan.

LEARNING PLAN:
{planning}

SOURCE MATERIAL:
{material}

STUDENT LEVEL: {level}
PACK TYPE: {pack_type}

Create:
# Quick Overview
# Core Concepts
# Key Terms
# Detailed Explanation
# Examples
# Common Misconceptions

Follow the plan, match the student's level, prioritize source material, and use Markdown.
"""

ASSESSMENT_SYSTEM = """You are an expert assessment designer. Create fair assessments that test genuine understanding."""

ASSESSMENT_PROMPT = """
Create assessments from the learning plan and generated content.

LEARNING PLAN:
{planning}

GENERATED CONTENT:
{content}

STUDENT LEVEL: {level}
Create exactly {flashcard_count} flashcards, {mcq_count} MCQs, and 5 short-answer questions.

Return ONLY valid JSON:
{{
  "flashcards": [{{"question": "...", "answer": "..."}}],
  "mcqs": [{{"question": "...", "options": ["A","B","C","D"], "correct_answer": "A", "explanation": "..."}}],
  "short_questions": ["question 1","question 2","question 3","question 4","question 5"]
}}
Every MCQ must have exactly four options and an unambiguous answer.
"""

REVIEW_SYSTEM = """You are a strict academic reviewer. Identify factual, structural, and assessment problems."""

REVIEW_PROMPT = """
Review these study-pack components.

PLAN:
{planning}

CONTENT:
{content}

ASSESSMENT:
{assessment}

Check factual accuracy, objective alignment, difficulty, missing concepts, redundancy,
ambiguous MCQs, incorrect answer keys, weak explanations, unsupported claims, and usefulness.

Return ONLY valid JSON:
{{
  "approved": true,
  "quality_score": 0,
  "content_issues": [],
  "assessment_issues": [],
  "missing_items": [],
  "recommended_changes": []
}}
Quality score must be 0-100.
"""

REFINEMENT_SYSTEM = """You are a senior educational editor. Correct and improve the study pack using review feedback."""

REFINEMENT_PROMPT = """
Create the final refined study pack.

PLAN:
{planning}

CONTENT:
{content}

ASSESSMENT:
{assessment}

REVIEW:
{review}

STUDENT LEVEL: {level}
Required flashcards: {flashcard_count}
Required MCQs: {mcq_count}

Apply the review feedback. Keep exactly the requested number of flashcards and MCQs.

Return Markdown with:
# AI Study Pack
## 1. Quick Overview
## 2. Learning Objectives
## 3. Core Concepts
## 4. Key Terms
## 5. Detailed Explanation
## 6. Examples
## 7. Flashcards
## 8. MCQ Quiz
## 9. Short-Answer Questions
## 10. Answer Key
## 11. Common Misconceptions
## 12. One-Day Revision Plan

Do not reveal MCQ answers before the answer key. Keep answers consistent with questions.
"""
