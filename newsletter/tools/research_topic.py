#!/usr/bin/env python3
"""
Research a topic using Perplexity API.

This tool performs web-grounded research using Perplexity's agent API,
returning structured information with citations for newsletter content.
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PerplexityAPIError(Exception):
    """Custom exception for Perplexity API errors."""
    pass

class ResearchTopicTool:
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise PerplexityAPIError("PERPLEXITY_API_KEY not found in environment")

        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Default model - can be overridden
        self.model = "llama-3.1-8b-instruct"

    def research(self, topic: str, system_prompt: Optional[str] = None,
                 max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Research a topic using Perplexity API.

        Args:
            topic: The topic to research
            system_prompt: Optional system prompt for context
            max_tokens: Optional max tokens for response

        Returns:
            Dictionary containing research results with citations
        """
        # Build the message payload
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": topic
        })

        payload = {
            "model": self.model,
            "messages": messages
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(
                f"{self.base_url}/v1/agent",
                headers=self.headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

            result = response.json()

            # Extract relevant information
            research_data = {
                "topic": topic,
                "model": self.model,
                "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "citations": result.get("choices", [{}])[0].get("message", {}).get("citations", []),
                "search_context": result.get("search_context", ""),
                "timestamp": datetime.now().isoformat(),
                "raw_response": result  # Keep for debugging
            }

            return research_data

        except requests.exceptions.RequestException as e:
            raise PerplexityAPIError(f"Perplexity API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise PerplexityAPIError(f"Failed to parse Perplexity API response: {str(e)}")
        except Exception as e:
            raise PerplexityAPIError(f"Unexpected error in Perplexity API call: {str(e)}")

    def research_with_context(self, topic: str, context: str) -> Dict[str, Any]:
        """
        Research with additional context.

        Args:
            topic: The topic to research
            context: Additional context or specific focus areas

        Returns:
            Dictionary containing research results
        """
        system_prompt = f"Additional context: {context}\n\nFocus on providing comprehensive information relevant to the newsletter."
        return self.research(topic, system_prompt)

    def save_result(self, result: Dict[str, Any], output_path: str = None) -> str:
        """
        Save research result to JSON file.

        Args:
            result: Research result dictionary
            output_path: Path to save file (default: ./.tmp/research_<topic>.json)

        Returns:
            Path where file was saved
        """
        if not output_path:
            # Sanitize topic for filename
            topic_slug = result.get("topic", "research").replace(" ", "_").replace("/", "_")
            output_path = f"./tmp/research_{topic_slug}.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return output_path

    def get_summary(self, result: Dict[str, Any]) -> str:
        """
        Get a concise summary of research results.

        Args:
            result: Research result dictionary

        Returns:
            Summary string
        """
        response = result.get("response", "")
        citations = result.get("citations", [])

        # Get first 3 sentences or 300 chars
        summary = response[:300] + "..." if len(response) > 300 else response

        if citations:
            summary += f"\n\nSources: {len(citations)} citation(s) found"

        return summary

def main():
    """CLI interface for the research tool."""
    if len(sys.argv) < 2:
        print("Usage: python research_topic.py <topic> [system_prompt] [max_tokens]")
        print("Example: python research_topic.py \"AI automation trends\" \"Focus on newsletter relevance\" 1000")
        return

    topic = sys.argv[1]
    system_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else None

    try:
        tool = ResearchTopicTool()

        print(f"Researching topic: {topic}")
        result = tool.research(topic, system_prompt, max_tokens)

        print("\n=== Research Results ===")
        print(f"Topic: {result['topic']}")
        print(f"Model: {result['model']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"\n=== Response ===")
        print(result['response'])

        if result['citations']:
            print(f"\n=== Citations ({len(result['citations'])}) ===")
            for i, citation in enumerate(result['citations'], 1):
                print(f"{i}. {citation}")

        # Save results
        output_path = tool.save_result(result)
        print(f"\nResults saved to: {output_path}")

        # Print summary
        summary = tool.get_summary(result)
        print(f"\n=== Summary ===")
        print(summary)

    except PerplexityAPIError as e:
        print(f"Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    exit(main())