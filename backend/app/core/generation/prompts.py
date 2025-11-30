"""Prompt templates for different query types."""


SYSTEM_PROMPT = """You are a helpful financial assistant for Qonfido, an AI Co-Pilot for Money.

Your role is to:
1. Answer questions about mutual funds and financial concepts
2. Provide accurate data from the retrieved context
3. Explain financial metrics clearly (CAGR, Sharpe ratio, volatility, etc.)
4. Be helpful but never give specific investment advice

Always base your answers on the provided context. If information is not in the context, acknowledge that."""


FAQ_PROMPT = """Based on the following FAQs, answer the user's question clearly and concisely.

## FAQ Context:
{context}

## Question:
{query}

## Instructions:
- Answer directly from the FAQ content
- Keep the response clear and educational
- If the exact answer isn't in the FAQs, say so
"""


NUMERICAL_PROMPT = """Based on the following fund performance data, answer the user's question about fund metrics.

## Fund Data:
{context}

## Question:
{query}

## Instructions:
- Include specific numbers and metrics in your answer
- List relevant funds with their key metrics (CAGR, Sharpe ratio, volatility, etc.)
- Format numbers clearly (e.g., "12.5% CAGR", "Sharpe ratio of 1.2")
- If comparing funds, present in a clear structure
- Acknowledge if data for some metrics is not available
"""


HYBRID_PROMPT = """Based on the following context (FAQs and fund data), provide a comprehensive answer.

## Context:
{context}

## Question:
{query}

## Instructions:
- Combine explanatory information from FAQs with specific fund data
- First explain concepts if needed, then provide specific examples/data
- Include relevant metrics when discussing funds
- Be comprehensive but concise
"""


def get_prompt_template(query_type: str) -> str:
    """Get prompt template for query type ('faq', 'numerical', or 'hybrid')."""
    templates = {
        "faq": FAQ_PROMPT,
        "numerical": NUMERICAL_PROMPT,
        "hybrid": HYBRID_PROMPT,
    }
    return templates.get(query_type, HYBRID_PROMPT)


def format_prompt(
    query: str,
    context: str,
    query_type: str = "hybrid",
) -> str:
    """Format prompt with query and context using appropriate template."""
    template = get_prompt_template(query_type)
    return template.format(query=query, context=context)
