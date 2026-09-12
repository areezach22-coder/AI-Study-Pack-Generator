import json
from prompts import (
    PLANNING_SYSTEM, PLANNING_PROMPT,
    CONTENT_SYSTEM, CONTENT_PROMPT,
    ASSESSMENT_SYSTEM, ASSESSMENT_PROMPT,
    REVIEW_SYSTEM, REVIEW_PROMPT,
    REFINEMENT_SYSTEM, REFINEMENT_PROMPT,
)


def call_ai(client, model, system_prompt, user_prompt, json_mode=False):
    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response.")

    return content


def parse_json(text):
    cleaned = text.strip()

    # Remove Markdown code fences if AI adds them
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```", "", 1)
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"AI returned invalid JSON. "
            f"The response may have been cut off. "
            f"JSON error: {error}"
        )


def create_context(
    topic,
    material,
    level,
    pack_type,
    flashcard_count,
    mcq_count,
    model,
):
    return {
        "input": {
            "topic": topic.strip(),
            "material": material.strip(),
            "level": level,
            "pack_type": pack_type,
            "flashcard_count": int(flashcard_count),
            "mcq_count": int(mcq_count),
        },
        "model": model,
        "planning": {},
        "content": {},
        "assessment": {},
        "review": {},
        "refinement": {},
        "workflow": {
            "completed_stages": [],
            "errors": [],
            "status": "Initialized",
        },
    }


def planning_stage(context, client):
    d = context["input"]

    result = call_ai(
        client,
        context["model"],
        PLANNING_SYSTEM,
        PLANNING_PROMPT.format(
            topic=d["topic"] or "Infer from material",
            material=d["material"] or "No material",
            level=d["level"],
            pack_type=d["pack_type"],
            flashcard_count=d["flashcard_count"],
            mcq_count=d["mcq_count"],
        ),
        json_mode=True,
    )

    context["planning"] = parse_json(result)
    context["workflow"]["completed_stages"].append("Planning")

    return context


def content_generation_stage(context, client):
    d = context["input"]

    result = call_ai(
        client,
        context["model"],
        CONTENT_SYSTEM,
        CONTENT_PROMPT.format(
            planning=json.dumps(context["planning"], indent=2),
            material=d["material"] or "No source material",
            level=d["level"],
            pack_type=d["pack_type"],
        ),
    )

    context["content"] = {
        "teaching_content": result
    }

    context["workflow"]["completed_stages"].append(
        "Content Generation"
    )

    return context


def assessment_stage(context, client):
    d = context["input"]

    result = call_ai(
        client,
        context["model"],
        ASSESSMENT_SYSTEM,
        ASSESSMENT_PROMPT.format(
            planning=json.dumps(context["planning"], indent=2),
            content=context["content"]["teaching_content"],
            level=d["level"],
            flashcard_count=d["flashcard_count"],
            mcq_count=d["mcq_count"],
        ),
        json_mode=True,
    )

    context["assessment"] = parse_json(result)
    context["workflow"]["completed_stages"].append("Assessment")

    return context


def review_stage(context, client):
    result = call_ai(
        client,
        context["model"],
        REVIEW_SYSTEM,
        REVIEW_PROMPT.format(
            planning=json.dumps(context["planning"], indent=2),
            content=context["content"]["teaching_content"],
            assessment=json.dumps(
                context["assessment"],
                indent=2
            ),
        ),
        json_mode=True,
    )

    context["review"] = parse_json(result)
    context["workflow"]["completed_stages"].append("Review")

    return context


def refinement_stage(context, client):
    d = context["input"]

    result = call_ai(
        client,
        context["model"],
        REFINEMENT_SYSTEM,
        REFINEMENT_PROMPT.format(
            planning=json.dumps(context["planning"], indent=2),
            content=context["content"]["teaching_content"],
            assessment=json.dumps(
                context["assessment"],
                indent=2
            ),
            review=json.dumps(
                context["review"],
                indent=2
            ),
            level=d["level"],
            flashcard_count=d["flashcard_count"],
            mcq_count=d["mcq_count"],
        ),
    )

    context["refinement"] = {
        "final_study_pack": result
    }

    context["workflow"]["completed_stages"].append(
        "Refinement"
    )

    return context


def run_workflow(context, client, progress_callback=None):

    stages = [
        ("Planning", planning_stage),
        ("Content Generation", content_generation_stage),
        ("Assessment", assessment_stage),
        ("Review", review_stage),
        ("Refinement", refinement_stage),
    ]

    for number, (name, function) in enumerate(stages, 1):

        if progress_callback:
            progress_callback(number, name)

        try:
            context = function(context, client)

        except Exception as error:

            context["workflow"]["errors"].append(
                f"{name}: {error}"
            )

            context["workflow"]["status"] = (
                f"{name} failed"
            )

            break

    if not context["workflow"]["errors"]:
        context["workflow"]["status"] = (
            "All stages completed"
        )

    return context
