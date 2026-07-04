import json

notebook_content = {
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק א׳ — הכנת סביבת העבודה במחברת\n",
        "הגדרת התלויות הבסיסיות. ניתן להשתמש במודל מקומי אם מותקן, אך כלול גם מימוש חלופי פשוט כדי שהמחברת תרוץ גם ללא שירות חיצוני."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 1 - imports\n",
        "import json\n",
        "import re\n",
        "from dataclasses import dataclass\n",
        "from typing import Dict, Any, Optional, List\n",
        "\n",
        "try:\n",
        "    import requests\n",
        "except ImportError:\n",
        "    requests = None"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ב׳ — הגדרת מבנה משותף לסוכנים\n",
        "כל סוכן יחזיר אובייקט אחיד הכולל את שם הסוכן, התוצאה, רמת הביטחון ופרטי מטא־דאטה. מבנה אחיד מקל על סוכן התזמור לחבר בין הרכיבים."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 2 - shared result object\n",
        "@dataclass\n",
        "class AgentResult:\n",
        "    agent_name: str\n",
        "    output: Any\n",
        "    confidence: float = 1.0\n",
        "    metadata: Optional[Dict[str, Any]] = None"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ג׳ — סוכן ניתוב לסיווג כוונות\n",
        "סוכן הניתוב מקבל את הודעת המשתמש ומחזיר כוונה ורמת ביטחון. נשתמש תחילה במימוש דטרמיניסטי פשוט כדי לאפשר בדיקות יציבות.\n",
        "\n",
        "**בדיקות לדוגמה:**"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 3 - router agent\n",
        "INTENTS = [\"generalChat\", \"analyzeReview\", \"summarizeText\", \"unknown\"]\n",
        "\n",
        "def router_agent(user_text: str) -> AgentResult:\n",
        "    text = user_text.lower()\n",
        "    if any(word in text for word in [\"review\", \"sentiment\"]):\n",
        "        intent, conf = \"analyzeReview\", 0.93\n",
        "    elif any(word in text for word in [\"summarize\", \"summary\"]):\n",
        "        intent, conf = \"summarizeText\", 0.90\n",
        "    elif len(text.strip()) < 4:\n",
        "        intent, conf = \"unknown\", 0.40\n",
        "    else:\n",
        "        intent, conf = \"generalChat\", 0.82\n",
        "    return AgentResult(\"RouterAgent\", {\"intent\": intent, \"confidence\": conf}, conf)\n",
        "\n",
        "# Cell 4 - router tests\n",
        "router_tests = [\n",
        "    \"Tell me a short joke\",\n",
        "    \"Analyze this review: The product is amazing\",\n",
        "    \"Summarize the following text\",\n",
        "    \"?\"\n",
        "]\n",
        "\n",
        "for text in router_tests:\n",
        "    result = router_agent(text)\n",
        "    print(text, \"=>\", result.output)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ד׳ — סוכן שפה מקומי\n",
        "סוכן השפה המקומי אחראי למשימות כלליות, כגון ניסוח קצר, שיחה פשוטה או סיכום בסיסי. במחברת ישנו מימוש חלופי כדי שהתרגיל יהיה ניתן להרצה בכל מחשב.\n",
        "\n",
        "**בדיקה לדוגמה:**"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 5 - optional Ollama call and safe fallback\n",
        "OLLAMA_URL = \"http://localhost:11434/api/generate\"\n",
        "OLLAMA_MODEL = \"llama3\"\n",
        "\n",
        "def call_ollama(prompt: str) -> Optional[str]:\n",
        "    if requests is None:\n",
        "        return None\n",
        "    try:\n",
        "        payload = {\"model\": OLLAMA_MODEL, \"prompt\": prompt, \"stream\": False}\n",
        "        response = requests.post(OLLAMA_URL, json=payload, timeout=20)\n",
        "        response.raise_for_status()\n",
        "        return response.json().get(\"response\", \"\").strip()\n",
        "    except Exception:\n",
        "        return None\n",
        "\n",
        "def local_llm_agent(prompt: str) -> AgentResult:\n",
        "    answer = call_ollama(prompt)\n",
        "    if not answer:\n",
        "        answer = \"Local fallback answer: I received the request and will answer briefly.\"\n",
        "    return AgentResult(\"LocalLLMAgent\", answer, 0.80)\n",
        "\n",
        "# Cell 6 - local agent test\n",
        "result = local_llm_agent(\"Tell me a short joke about AI agents\")\n",
        "print(result.agent_name)\n",
        "print(result.output)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ה׳ — סוכן כלי ייעודי לניתוח סנטימנט\n",
        "במקום להרים שירות נפרד, נבנה את כלי הסנטימנט ישירות בתוך המחברת. ניתן להשתמש אם החבילה מותקנת.\n",
        "\n",
        "**בדיקות לדוגמה:**"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 7 - sentiment agent with optional transformers\n",
        "try:\n",
        "    from transformers import pipeline\n",
        "    sentiment_pipeline = pipeline(\"sentiment-analysis\")\n",
        "except Exception:\n",
        "    sentiment_pipeline = None\n",
        "\n",
        "def rule_based_sentiment(text: str) -> Dict[str, Any]:\n",
        "    positive = [\"good\", \"great\", \"amazing\", \"excellent\", \"love\"]\n",
        "    negative = [\"bad\", \"terrible\", \"awful\", \"hate\", \"poor\"]\n",
        "    lower = text.lower()\n",
        "    if any(w in lower for w in positive):\n",
        "        return {\"sentiment\": \"POSITIVE\", \"confidence\": 0.85}\n",
        "    if any(w in lower for w in negative):\n",
        "        return {\"sentiment\": \"NEGATIVE\", \"confidence\": 0.85}\n",
        "    return {\"sentiment\": \"NEUTRAL\", \"confidence\": 0.60}\n",
        "\n",
        "def sentiment_agent(text: str) -> AgentResult:\n",
        "    if sentiment_pipeline:\n",
        "        result = sentiment_pipeline(text)[0]\n",
        "        output = {\n",
        "            \"sentiment\": result[\"label\"],\n",
        "            \"confidence\": round(float(result[\"score\"]), 3)\n",
        "        }\n",
        "    else:\n",
        "        output = rule_based_sentiment(text)\n",
        "    return AgentResult(\"SentimentAnalysisAgent\", output, output[\"confidence\"])\n",
        "\n",
        "# Cell 8 - sentiment tests\n",
        "samples = [\n",
        "    \"The product is amazing and I love it\",\n",
        "    \"This is terrible and very disappointing\",\n",
        "    \"The product arrived yesterday\"\n",
        "]\n",
        "for sample in samples:\n",
        "    print(sample, \"=>\", sentiment_agent(sample).output)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ו׳ — בחירת כלים\n",
        "הסוכן אינו רק מייצר טקסט. עליו לבחור כלי מתאים לפי הכוונה ורמת הביטחון. זהו ההבדל המרכזי בין קריאה רגילה למודל לבין מערכת סוכנים.\n",
        "\n",
        "**בדיקות לדוגמה:**"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 9 - tool selection\n",
        "TOOLS = {\n",
        "    \"local_llm\": \"general chat and simple summarization\",\n",
        "    \"sentiment_analyzer\": \"sentiment analysis for reviews\",\n",
        "    \"cloud_fallback\": \"fallback when confidence is low\"\n",
        "}\n",
        "\n",
        "def select_tool(intent: str, confidence: float) -> str:\n",
        "    if confidence < 0.80:\n",
        "        return \"cloud_fallback\"\n",
        "    if intent == \"analyzeReview\":\n",
        "        return \"sentiment_analyzer\"\n",
        "    if intent in [\"generalChat\", \"summarizeText\"]:\n",
        "        return \"local_llm\"\n",
        "    return \"cloud_fallback\"\n",
        "\n",
        "# Cell 10 - tool selection tests\n",
        "cases = [\n",
        "    (\"generalChat\", 0.82),\n",
        "    (\"analyzeReview\", 0.93),\n",
        "    (\"summarizeText\", 0.90),\n",
        "    (\"unknown\", 0.40)\n",
        "]\n",
        "for intent, confidence in cases:\n",
        "    print(intent, confidence, \"=>\", select_tool(intent, confidence))"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ז׳ — סוכן תזמור מרכזי\n",
        "סוכן התזמור מחבר את כל המערכת: הוא מקבל את הודעת המשתמש, מפעיל את סוכן הניתוב, בוחר כלי, מפעיל את הסוכן המתאים ומחזיר תשובה סופית.\n",
        "\n",
        "**בדיקות אינטגרציה לדוגמה:**"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 11 - orchestrator agent\n",
        "agent_memory = {\n",
        "    \"last_intent\": None,\n",
        "    \"last_tool\": None,\n",
        "    \"last_user_message\": None,\n",
        "    \"last_result\": None\n",
        "}\n",
        "\n",
        "def cloud_fallback_agent(user_text: str) -> AgentResult:\n",
        "    answer = \"Fallback answer: the request is unclear or confidence is too low.\"\n",
        "    return AgentResult(\"CloudFallbackAgent\", answer, 0.70)\n",
        "\n",
        "def orchestrator_agent(user_text: str) -> AgentResult:\n",
        "    route = router_agent(user_text)\n",
        "    intent = route.output[\"intent\"]\n",
        "    confidence = route.output[\"confidence\"]\n",
        "    tool = select_tool(intent, confidence)\n",
        "\n",
        "    if tool == \"sentiment_analyzer\":\n",
        "        result = sentiment_agent(user_text)\n",
        "    elif tool == \"local_llm\":\n",
        "        result = local_llm_agent(user_text)\n",
        "    else:\n",
        "        result = cloud_fallback_agent(user_text)\n",
        "\n",
        "    agent_memory.update({\n",
        "        \"last_intent\": intent,\n",
        "        \"last_tool\": tool,\n",
        "        \"last_user_message\": user_text,\n",
        "        \"last_result\": result.output\n",
        "    })\n",
        "    return result\n",
        "\n",
        "# Cell 12 - integration tests\n",
        "messages = [\n",
        "    \"Tell me a short joke\",\n",
        "    \"Analyze this review: The product is amazing\",\n",
        "    \"Summarize the following paragraph\",\n",
        "    \"?\"\n",
        "]\n",
        "for msg in messages:\n",
        "    result = orchestrator_agent(msg)\n",
        "    print(\"USER:\", msg)\n",
        "    print(\"AGENT:\", result.agent_name)\n",
        "    print(\"OUTPUT:\", result.output)\n",
        "    print(\"MEMORY:\", agent_memory)\n",
        "    print(\"---\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ח׳ — זיכרון קצר טווח\n",
        "הזיכרון מאפשר לסוכן להבין בקשות המשך. לדוגמה, לאחר ניתוח ביקורת, המשתמש יכול לשאול: \"למה?\" והמערכת תוכל להתייחס לתוצאה הקודמת."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 13 - memory follow-up example\n",
        "orchestrator_agent(\"Analyze this review: The product is amazing\")\n",
        "print(agent_memory)\n",
        "follow_up = \"Why?\"\n",
        "if agent_memory[\"last_intent\"] == \"analyzeReview\":\n",
        "    print(\"Explanation: positive words in the review indicate positive sentiment.\")\n",
        "else:\n",
        "    print(\"No relevant previous context was found.\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק ט׳ — סוכן ביקורת\n",
        "סוכן הביקורת מעריך את איכות התשובה של סוכן אחר. אם הציון נמוך מ־3, סוכן התזמור צריך להפעיל גיבוי."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 14 - critic agent\n",
        "def critic_agent(answer: Any) -> AgentResult:\n",
        "    text = str(answer)\n",
        "    if len(text.strip()) < 20:\n",
        "        score = 2\n",
        "    elif \"example\" in text.lower() or \"POSITIVE\" in text or \"NEGATIVE\" in text:\n",
        "        score = 4\n",
        "    else:\n",
        "        score = 3\n",
        "    return AgentResult(\"CriticAgent\", {\"quality_score\": score}, score / 5)\n",
        "\n",
        "# Example\n",
        "answer = local_llm_agent(\"Say something short\").output\n",
        "critique = critic_agent(answer)\n",
        "print(answer)\n",
        "print(critique.output)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### חלק י׳ — בדיקות מסכמות במחברת\n",
        "בסוף המחברת יש להוסיף תא בדיקות מסכם. התא צריך להריץ מספר תרחישים ולוודא שכל רכיבי המערכת עובדים יחד."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Cell 15 - final validation\n",
        "final_tests = [\n",
        "    (\"Tell me a short joke\", \"LocalLLMAgent\"),\n",
        "    (\"Analyze this review: This product is terrible\", \"SentimentAnalysisAgent\"),\n",
        "    (\"?\", \"CloudFallbackAgent\")\n",
        "]\n",
        "for message, expected_agent in final_tests:\n",
        "    result = orchestrator_agent(message)\n",
        "    assert result.agent_name == expected_agent, (message, result.agent_name, expected_agent)\n",
        "    print(\"PASS:\", message, \"=>\", result.agent_name)\n",
        "print(\"All final tests passed\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### סיכום התרגיל\n",
        "\n",
        "* **מה עבד היטב:** חלוקת האחריות לארכיטקטורה של סוכנים (נתב, מנתח סנטימנט, ומודל שיחה) הקלה על פיתוח המערכת וניהול הזרימה. התזמור בין הרכיבים איפשר לנתב שאילתות בדיוק למקום המתאים.\n",
        "* **מה היה מוגבל:** סוכן הניתוב שלנו הסתמך על חוקיות נוקשה (if-else) שהיא מוגבלת מאוד בהשוואה להבנת שפה טבעית. כמו כן, מימוש הסנטימנט מבוסס החוקים יכול בקלות לפספס ניואנסים או משפטים מורכבים.\n",
        "* **מתי כדאי להשתמש במודל מקומי לעומת שירות ענן:** כדאי להשתמש במודל מקומי כאשר יש צורך בשמירה על פרטיות הנתונים, חיסכון בעלויות API חיצוניות וכאשר המשימה פשוטה מספיק. שירות ענן עדיף כאשר נדרשים ביצועים גבוהים, זמני תגובה מהירים מאוד ללא עומס על חומרת הקצה, או כשיש צורך להשתמש במודלי שפה מתקדמים וכבדים בעלי יכולות הסקה מורכבות."
      ]
    }
  ],
  "metadata": {
    "language_info": {
      "name": "python",
      "version": "3.9"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}

with open("agentic_ai_exercise.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, ensure_ascii=False, indent=2)

print("✅ יצירת המחברת הושלמה בהצלחה! תוכלי לפתוח את הקובץ agentic_ai_exercise.ipynb שנוצר עכשיו בצד שמאל.")