"""
LLM Prompt Templates for AI Audit Analysis
"""


def get_audit_analysis_prompt(company_data: dict) -> str:
    """
    Generate the system prompt for AI audit analysis.
    
    Args:
        company_data: Dictionary containing company information and department data
        
    Returns:
        Formatted prompt string for the LLM
    """
    
    # Extract company information
    company_name = company_data.get('company_name', 'Unknown Company')
    industry = company_data.get('industry', 'Unknown Industry')
    company_size = company_data.get('company_size', 'Unknown Size')
    annual_revenue = company_data.get('annual_revenue_inr', 'Unknown Revenue')
    departments = company_data.get('departments', {})
    
    # Format department data
    dept_details = []
    for dept_name, dept_data in departments.items():
        dept_str = f"\n{dept_name}:"
        if isinstance(dept_data, dict):
            for key, value in dept_data.items():
                dept_str += f"\n  - {key}: {value}"
        dept_details.append(dept_str)
    
    departments_text = "\n".join(dept_details)
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert AI Business Auditor specializing in digital transformation and AI maturity assessment. You provide detailed, objective analysis in JSON format.<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze the following company data and return ONLY valid JSON. Do not include any explanatory text, markdown formatting, or code blocks - just the raw JSON object.

COMPANY INFORMATION:
- Company Name: {company_name}
- Industry: {industry}
- Company Size: {company_size}
- Annual Revenue: {annual_revenue}

DEPARTMENT-WISE DATA:
{departments_text}

Your output MUST be a valid JSON object with the following structure:
{{
  "summary": {{
    "personalized_summary": "A concise 3-4 sentence paragraph analyzing the company's AI maturity. Reference the company name, industry, and size. Identify key gaps and limitations without suggesting improvements.",
    "overall_risk_score": <integer between 0-100, where higher = more risk/less AI maturity>,
    "ai_maturity_level": "<Low/Medium/High>"
  }},
  "sections": [
    {{
      "section_name": "<Department Name>",
      "level": "<Low/Medium/High>",
      "drawbacks": [
        {{
          "title": "<Brief drawback title>",
          "details": "<1-2 sentence explanation of the limitation or gap>"
        }}
      ]
    }}
  ]
}}

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown formatting, no code blocks, no extra text
2. The "personalized_summary" MUST reference the company name ({company_name}), industry ({industry}), and company size
3. Focus ONLY on limitations, gaps, and drawbacks - DO NOT suggest improvements or solutions
4. Each department should have a "level" (Low/Medium/High) indicating AI maturity
5. "overall_risk_score" should be 0-100 (0=fully mature, 100=no AI adoption)
6. Include at least 1-2 drawbacks per department where applicable
7. If a department shows good maturity, it can have an empty drawbacks array
8. Be specific and reference actual data points from the department information
9. Keep titles concise (5-8 words) and details informative (1-2 sentences)

ASSESSMENT CRITERIA:
- Low Maturity: Manual processes, no automation, no data analytics, legacy systems
- Medium Maturity: Some digital tools, basic automation, limited analytics, reactive approach
- High Maturity: Advanced automation, AI/ML integration, proactive analytics, modern infrastructure

Now analyze the data and return ONLY the JSON response:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    return prompt


def get_system_instructions() -> str:
    """
    Get general system instructions for the LLM.
    
    Returns:
        System instruction string
    """
    return """You are an AI Business Auditor. You analyze companies' digital and AI maturity levels.
Your responses must be:
1. In valid JSON format only
2. Focused on identifying gaps and limitations
3. Based on evidence from provided data
4. Professional and objective
5. Without recommendations or solutions

Remember: Return ONLY valid JSON without any markdown formatting or additional text."""
