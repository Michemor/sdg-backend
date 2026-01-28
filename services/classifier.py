"""
SDG Activity Classifier Service
Uses Google Generative AI (Gemini) to automatically classify activities
and determine their relevance to Sustainable Development Goals.
"""

import json
import logging
import os
from typing import List, Dict, Any

try:
    import google.generativeai as genai  # type: ignore
except ImportError as e:
    raise ImportError(
        "google-generativeai package not found. "
        "Please install it using: pip install google-generativeai"
    ) from e


logger = logging.getLogger(__name__)


class SDGClassifier:
    """Service for classifying activities using Gemini AI."""

    def __init__(self, api_key: str = None):
        """
        Initialize the classifier with Gemini API key.
        
        Args:
            api_key: Google Generative AI API key. If None, reads from GEMINI_API_KEY env var.
        """
        api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        if not api_key:
            logger.warning("GEMINI_API_KEY not configured. AI classification will fail.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def classify_activity_sdg(
        self,
        title: str,
        description: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Classify an activity against the 17 UN Sustainable Development Goals.
        
        Args:
            title: Title of the activity
            description: Detailed description of the activity
            max_results: Maximum number of SDGs to return (top matches)
        
        Returns:
            List of dictionaries with keys:
                - sdg_number: int (1-17)
                - relevance_score: int (0-100)
                - justification: str (reasoning for the score)
        
        Raises:
            ValueError: If API response cannot be parsed as JSON
            Exception: If API call fails
        """
        try:
            # Construct the prompt with strict JSON formatting instructions
            prompt = self._build_classification_prompt(title, description, max_results)
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse the JSON response
            impacts = self._parse_json_response(response_text)
            
            logger.info(f"Successfully classified activity '{title}' to {len(impacts)} SDGs")
            return impacts
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Error during SDG classification: {str(e)}")
            raise

    def _build_classification_prompt(self, title: str, description: str, max_results: int) -> str:
        """Build the prompt for Gemini with strict JSON formatting."""
        return f"""Analyze the following university activity and determine its relevance to the UN Sustainable Development Goals (SDGs).

Activity Title: {title}

Activity Description: {description}

Instructions:
1. Evaluate the activity against all 17 SDGs
2. Identify the top {max_results} most relevant SDGs
3. For each SDG, provide:
   - SDG number (1-17)
   - A relevance score from 0-100 (where 100 is extremely relevant)
   - A brief justification for the score

IMPORTANT: Respond ONLY with valid JSON (no markdown, no code blocks, no extra text). The JSON structure must be exactly:

{{
  "impacts": [
    {{"sdg_number": 1, "relevance_score": 85, "justification": "Clear explanation here"}},
    {{"sdg_number": 3, "relevance_score": 72, "justification": "Another explanation"}}
  ]
}}

Return only the JSON object, nothing else."""

    def _parse_json_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse the JSON response from Gemini.
        
        Args:
            response_text: Raw text response from Gemini
        
        Returns:
            List of impact dictionaries
        
        Raises:
            ValueError: If response cannot be parsed
        """
        # Try to extract JSON from the response
        # Sometimes the model wraps it in markdown code blocks
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse JSON
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # If still failing, try to find JSON object in the text
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("Could not extract valid JSON from response")
        
        # Extract impacts list
        if not isinstance(data, dict) or 'impacts' not in data:
            raise ValueError("Response JSON must contain an 'impacts' key")
        
        impacts = data['impacts']
        
        if not isinstance(impacts, list):
            raise ValueError("'impacts' must be a list")
        
        # Validate each impact entry
        for impact in impacts:
            if not isinstance(impact, dict):
                raise ValueError("Each impact must be a dictionary")
            
            required_keys = {'sdg_number', 'relevance_score', 'justification'}
            if not required_keys.issubset(impact.keys()):
                raise ValueError(f"Each impact must contain: {required_keys}")
            
            # Validate types and ranges
            if not isinstance(impact['sdg_number'], int) or not (1 <= impact['sdg_number'] <= 17):
                raise ValueError(f"sdg_number must be integer 1-17, got {impact['sdg_number']}")
            
            if not isinstance(impact['relevance_score'], int) or not (0 <= impact['relevance_score'] <= 100):
                raise ValueError(f"relevance_score must be integer 0-100, got {impact['relevance_score']}")
            
            if not isinstance(impact['justification'], str):
                raise ValueError("justification must be a string")
        
        return impacts


# Singleton instance for easy access
_classifier = None


def get_classifier(api_key: str = None) -> SDGClassifier:
    """Get or create the singleton classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = SDGClassifier(api_key)
    return _classifier


def classify_activity_sdg(title: str, description: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to classify an activity.
    
    Args:
        title: Activity title
        description: Activity description
        max_results: Maximum number of SDGs to return
    
    Returns:
        List of impact dictionaries
    """
    classifier = get_classifier()
    return classifier.classify_activity_sdg(title, description, max_results)
