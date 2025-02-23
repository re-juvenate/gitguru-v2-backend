import aiohttp
import asyncio
from urllib.parse import urljoin
import json
import argparse

async def searxng_search(
    searx_url: str,
    query: str,
    language: str = 'en-US',
    max_results: int = 10
) -> list[dict]:
    """
    Async SearxNG search returning titles/snippets/urls
    """
    search_endpoint = urljoin(searx_url, '/search')
    params = {
        'q': query,
        'format': 'json',
        'language': language,
        'pageno': 1,
        'count': max_results,
        'category': 'general',
        'safesearch': 0
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                search_endpoint,
                params=params,
                headers={'Accept': 'application/json'}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return [{
                    'title': result.get('title', ''),
                    'snippet': result.get('content', ''),
                    'url': result.get('url', '')
                } for result in data.get('results', [])]

        except aiohttp.ClientError as e:
            print(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            print("Invalid JSON response")
        except KeyError:
            print("Unexpected response format")
            
        return []

async def main():
    parser = argparse.ArgumentParser(description='Async SearxNG Search')
    parser.add_argument('--searx-url', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--max-results', type=int, default=5)
    args = parser.parse_args()

    results = await searxng_search(
        args.searx_url,
        args.query,
        max_results=args.max_results
    )

    print(f"Found {len(results)} results:")
    for idx, result in enumerate(results, 1):
        print(f"\n{idx}. {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Snippet: {result['snippet'][:150]}...\n")
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(main())