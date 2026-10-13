from src.cred_support_agent.cache.response_cache import ResponseCache


def test_response_cache_normalizes_query_and_hits():
    cache = ResponseCache()
    original = {"answer": "cached answer"}
    cache.set(" What are loan EMIs? ", original)
    assert cache.get("what are loan emis?") == original
    assert cache.get("WHAT ARE LOAN EMIS?") == original
