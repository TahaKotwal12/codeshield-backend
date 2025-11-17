import google.generativeai as genai
from app.config.config import GEMINI_CONFIG
from app.config.logger import get_logger
from app.api.schemas.analyze_schemas import Vulnerability, Fix, RiskScore, Severity
import json
import re

logger = get_logger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini API for code analysis."""
    
    def __init__(self):
        """Initialize Gemini service with API key."""
        api_key = GEMINI_CONFIG["api_key"]
        if not api_key:
            logger.error("GEMINI_API_KEY is not set in environment variables")
            raise ValueError("GEMINI_API_KEY is not set in environment variables. Please set it in your .env file or Vercel environment variables.")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_CONFIG["model"])
            self.temperature = GEMINI_CONFIG["temperature"]
            logger.info("Gemini service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini service: {str(e)}")
    
    def analyze_code(self, code: str) -> dict:
        """
        Analyze code for security vulnerabilities using Gemini AI.
        
        Args:
            code: The code to analyze
            
        Returns:
            Dictionary containing vulnerabilities, fixes, risk_score, and explanation
        """
        try:
            prompt = self._build_analysis_prompt(code)
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": GEMINI_CONFIG["max_tokens"],
                }
            )
            
            result_text = response.text
            logger.info("Gemini analysis completed successfully")
            
            # Parse the response
            return self._parse_response(result_text, code)
            
        except Exception as e:
            logger.error(f"Error analyzing code with Gemini: {str(e)}")
            raise Exception(f"Failed to analyze code: {str(e)}")
    
    def _build_analysis_prompt(self, code: str) -> str:
        """Build the prompt for code analysis."""
        return f"""You are a security code analyzer. Analyze the following code for security vulnerabilities and provide a comprehensive security assessment.

Code to analyze:
```python
{code}
```

Please provide your analysis in the following JSON format:
{{
    "vulnerabilities": [
        {{
            "line": <line_number>,
            "severity": "High|Medium|Low",
            "type": "<vulnerability_type>",
            "description": "<detailed_description>"
        }}
    ],
    "fixes": [
        {{
            "line": <line_number>,
            "original": "<original_code>",
            "fixed": "<fixed_code>",
            "explanation": "<explanation_of_fix>"
        }}
    ],
    "risk_score": "High|Medium|Low",
    "explanation": "<comprehensive_explanation_of_overall_security_assessment>"
}}

Important guidelines:
1. Identify all security vulnerabilities (SQL injection, XSS, authentication issues, insecure dependencies, etc.)
2. Provide specific line numbers for each vulnerability
3. For each vulnerability, provide a fix with the original and fixed code
4. Assign appropriate severity levels (High, Medium, Low)
5. Calculate overall risk_score based on the severity and number of vulnerabilities
6. Provide a detailed explanation of the security assessment
7. If no vulnerabilities are found, return empty arrays and set risk_score to "Low"
8. Ensure the response is valid JSON

Return ONLY the JSON object, no additional text or markdown formatting."""

    def _parse_response(self, response_text: str, original_code: str) -> dict:
        """Parse Gemini response and extract structured data."""
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            try:
                parsed = json.loads(cleaned_text)
            except json.JSONDecodeError:
                # Try to extract JSON from the text if it's embedded
                json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from response")
            
            # Validate and structure the response
            vulnerabilities = []
            for vuln in parsed.get("vulnerabilities", []):
                try:
                    vulnerabilities.append({
                        "line": int(vuln.get("line", 1)),
                        "severity": vuln.get("severity", "Medium"),
                        "type": vuln.get("type", "Unknown"),
                        "description": vuln.get("description", "")
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid vulnerability entry: {e}")
                    continue
            
            fixes = []
            for fix in parsed.get("fixes", []):
                try:
                    fixes.append({
                        "line": int(fix.get("line", 1)),
                        "original": fix.get("original", ""),
                        "fixed": fix.get("fixed", ""),
                        "explanation": fix.get("explanation", "")
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid fix entry: {e}")
                    continue
            
            risk_score = parsed.get("risk_score", "Medium")
            if risk_score not in ["High", "Medium", "Low"]:
                risk_score = "Medium"
            
            explanation = parsed.get("explanation", "Security analysis completed.")
            
            return {
                "vulnerabilities": vulnerabilities,
                "fixes": fixes,
                "risk_score": risk_score,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            # Return a safe default response
            return {
                "vulnerabilities": [],
                "fixes": [],
                "risk_score": "Low",
                "explanation": f"Analysis completed but encountered an error parsing results: {str(e)}"
            }


