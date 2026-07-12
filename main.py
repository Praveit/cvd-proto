import os
import re
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from functools import wraps
from urllib.parse import urljoin

# =============================================================================
# 1. DATA FRAMEWORK & MODELS
# =============================================================================

class Organization:
    """Tracks business accounts and their associated target/competitor brand keywords."""
    def __init__(self, org_id: int, name: str, brand_keywords: List[str]):
        self.org_id = org_id
        self.name = name
        self.brand_keywords = brand_keywords

# =============================================================================
# 2. API CORE & RESILIENCE HANDLERS
# =============================================================================

DEFAULT_API_BASE_URL = "https://api.openai.com/v1"
RETRY_COUNT = 3
BACKOFF_FACTOR = 0.5

def retry_api_calls(num_retries: int = RETRY_COUNT, backoff_factor: float = BACKOFF_FACTOR):
    """Decorator supplying custom retry logic with exponential backoff for resilience."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, num_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    if attempt < num_retries:
                        sleep_time = attempt * backoff_factor
                        print(f"[Warning] Error during attempt {attempt}. Retrying in {sleep_time}s... Error: {e}")
                        await asyncio.sleep(sleep_time)
                    else:
                        print(f"[Critical] All {num_retries} api retries failed.")
                        raise e
            return None
        return wrapper
    return decorator


class AIInterrogation:
    """Handles secure proxy connectivity and raw data retrieval from the target LLM layer."""
    def __init__(self, api_key: str):
        self._api_key = api_key

    @retry_api_calls()
    async def create_completion(self, prompt: str, model: str = 'text-davinci-002') -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self._api_key}',
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt.strip(),
            "model": model,
            "temperature": 0.0  
        }
        
        async with aiohttp.ClientSession() as session:
            url = urljoin(DEFAULT_API_BASE_URL, "/completions")
            async with session.post(url, headers=headers, json=payload) as response:
                if (response.status // 100) != 2:
                    try:
                        error_payload = await response.json()
                        error_msg = error_payload.get('error', {}).get('message', 'Unknown API Error')
                    except Exception:
                        error_msg = await response.text()
                    raise Exception(f"API request failed: [{response.status}] {error_msg}")
                
                result = await response.json()
                return result

# =============================================================================
# 3. MICRO-EVALUATOR & NLP PIPELINE (Strict Schema Parser)
# =============================================================================

def extract_brand_entities(raw_response: str, registered_keywords: List[str]) -> List[str]:
    """Scans response strings using clear regex boundary markers to compute registry intersections."""
    found_entities = []
    for keyword in registered_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, raw_response, re.IGNORECASE):
            found_entities.append(keyword)
    return found_entities


def calculate_mention_rank(raw_response: str, entity: str) -> Optional[int]:
    """Computes individual occurrence position indexing based on sentence-split hierarchies."""
    sentences = re.split(r'(?<=[.!?])\s+', raw_response)
    for idx, sentence in enumerate(sentences):
        if re.search(r'\b' + re.escape(entity) + r'\b', sentence, re.IGNORECASE):
            return idx + 1  
    return None


def calculate_sentiment_score(raw_response: str, entity: str) -> float:
    """Analyzes sentence-localized string signifiers to calculate a dynamic evaluation score."""
    sentences = re.split(r'(?<=[.!?])\s+', raw_response)
    target_sentence = ""
    
    # Isolate the exact sentence containing the brand keyword for contextual analysis
    for sentence in sentences:
        if re.search(r'\b' + re.escape(entity) + r'\b', sentence, re.IGNORECASE):
            target_sentence = sentence.lower()
            break
            
    if not target_sentence:
        return 0.00

    positive_signals = ["best", "highly", "efficient", "love", "great", "pristine", "optimized", "speed"]
    negative_signals = ["struggles", "fail", "slow", "placeholder", "buggy", "critical", "complexity"]
    
    score = 0.0
    for word in positive_signals:
        if word in target_sentence:
            score += 0.25
    for word in negative_signals:
        if word in target_sentence:
            score -= 0.25
            
    return max(-1.00, min(1.00, round(score, 2)))


def extract_citations(raw_response: str) -> List[str]:
    """Finds inline URLs and cleans off common trailing sentence punctuation."""
    raw_urls = re.findall(r'https?://[^\s)\]]+', raw_response)
    cleaned_urls = []
    for url in raw_urls:
        # Strip trailing trailing periods, commas, or colons left behind by text regex splits
        cleaned_url = re.sub(r'[.,;:]+$', '', url)
        cleaned_urls.append(cleaned_url)
    return list(set(cleaned_urls))


def evaluate_response(raw_response: str, registered_keywords: List[str]) -> Dict[str, Any]:
    """Aggregates low-level modular extractions into the final compliant metrics registry schema."""
    detected = extract_brand_entities(raw_response, registered_keywords)
    citations = extract_citations(raw_response)
    
    primary_brand = registered_keywords[0] if registered_keywords else "Unknown"
    brand_mentioned = primary_brand in detected
    
    mention_rank = calculate_mention_rank(raw_response, primary_brand) if brand_mentioned else None
    sentiment = calculate_sentiment_score(raw_response, primary_brand) if brand_mentioned else 0.00
    
    return {
        "entity_extractions": {
            "brand_entities": [
                {
                    "id": f"brand_{idx}",
                    "value": entity,
                    "sentiment_score": calculate_sentiment_score(raw_response, entity),
                    "mention_rank": calculate_mention_rank(raw_response, entity)
                } for idx, entity in enumerate(detected)
            ],
            "raw_text_citations": [{"url": link} for link in citations]
        },
        "summary_metrics": {
            "brand_mentioned": brand_mentioned,
            "primary_brand_rank": mention_rank,
            "primary_brand_sentiment": sentiment,
            "total_citations_found": len(citations)
        }
    }

# =============================================================================
# 4. EXECUTABLE END-TO-END DEMONSTRATION WORKFLOW
# =============================================================================

async def main():
    org = Organization(org_id=1, name="Linear App Group", brand_keywords=["Linear", "Jira", "Asana"])
    
    mock_llm_response = (
        "When evaluating the Top 10 Best Issue Trackers for Startups, Linear stands out as "
        "the absolute best tool due to its pristine optimization and clean speed. "
        "Conversely, Jira struggles with setup complexity and can feel slow during deployment loops. "
        "For additional information, see our tracking architecture breakdown at https://linear.app/blog."
    )
    
    print("=============================================================================")
    print("RUNNING DEMONSTRATION ENGINE EVALUATION PIPELINE")
    print("=============================================================================\n")
    print(f"Mock Engine Response Received:\n\"{mock_llm_response}\"\n")
    
    scan_result_payload = evaluate_response(mock_llm_response, org.brand_keywords)
    
    final_output_schema = {
        "scan_results": {
            "id": 10042,
            "engine_name": "ChatGPT-4o (Simulated)",
            "organization_id": org.org_id,
            "payload": scan_result_payload
        }
    }
    
    print("Compliant Output Schema JSON Summary:")
    print(json.dumps(final_output_schema, indent=4))
    
    os.makedirs("output", exist_ok=True)
    output_filepath = "output/scan_results.json"
    with open(output_filepath, "w") as target_file:
        json.dump(final_output_schema, target_file, indent=4)
    print(f"\n[Success] Execution complete. File saved to: {os.path.abspath(output_filepath)}")

if __name__ == "__main__":
    asyncio.run(main())