from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
from django.conf import settings
import logging
import json
from langchain.agents import  create_agent
from langchain_core.prompts import PromptTemplate


logger = logging.getLogger(__name__)
class ScrapingAgent:
    def __init__ (self, scarpped_data: dict):
        self.scrapped_data = scarpped_data
        self.llm = self._setup_llm()
    
    def _setup_llm(self):
        try:
            llm = ChatGroq(
                groq_api_key = settings.GROQ_API_KEY,
                temperature = 0.1,
                max_tokens=4046,

            )
            logger.info(f"LLM initialized ")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise


            
    def extract_structured_data(self, user_instructions: str) -> dict:
        """
        Extract structured data based on user instructions
        
        Args:
            user_instructions: Natural language instructions from user
            
        Returns:
            Structured data extracted by AI
        """
        try:
            # Prepare the data summary for the LLM
            data_summary = self._prepare_data_summary()
            
            # Create the prompt
            prompt = f"""You are an expert web scraping assistant. You have been given scraped data from a website and user instructions on what to extract.

**Scraped Data Summary:**
{data_summary}

**User Instructions:**
{user_instructions}

**Your Task:**
Based on the scraped data and user instructions, extract and structure the relevant information. Return your response as a JSON object with clear keys and values.

If the user wants specific fields (like product names, prices, titles, etc.), create appropriate JSON structure.
If no specific instructions are given, provide a useful summary of the most important information.

**Important:**
- Only include information that exists in the scraped data
- Structure the data logically
- Use clear, descriptive keys
- If certain requested information is not found, indicate that in your response

Return ONLY valid JSON, no additional text."""

            # Call the LLM
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse the response
            result = self._parse_llm_response(response.content)
            
            logger.info("Successfully extracted structured data")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract structured data: {str(e)}")
            return {
                "error": str(e),
                "raw_data": self.scraped_data
            }
    
    def _prepare_data_summary(self) ->str:
        """Prepare consise Summary of scrapped data for LLM"""
        summary = []

        if self.scraped_data.get('title'):
            summary.append(f"Title: {self.scraped_data['title']}")
        
        # Meta description
        if self.scraped_data.get('meta_description'):
            summary.append(f"Description: {self.scraped_data['meta_description']}")
        
        # Headings
        headings = self.scraped_data.get('headings', {})
        for tag, texts in headings.items():
            if texts:
                summary.append(f"{tag.upper()}: {', '.join(texts[:5])}")
        
        # Links (sample)
        links = self.scraped_data.get('links', [])
        if links:
            summary.append(f"Links found: {len(links)} links")
            summary.append("Sample links:")
            for link in links[:5]:
                summary.append(f"  - {link.get('text', 'No text')}: {link.get('url', '')}")
        
        # Images (sample)
        images = self.scraped_data.get('images', [])
        if images:
            summary.append(f"Images found: {len(images)} images")
        
        # Text content (truncated)
        text_content = self.scraped_data.get('text_content', '')
        if text_content:
            summary.append(f"Text content (first 1000 chars): {text_content[:1000]}")
        
        # Tables
        tables = self.scraped_data.get('tables', [])
        if tables:
            summary.append(f"Tables found: {len(tables)} tables")
            summary.append("First table sample:")
            if tables[0]:
                for row in tables[0][:3]:
                    summary.append(f"  {row}")
        
        # Lists
        lists = self.scraped_data.get('lists', {})
        if lists.get('unordered'):
            summary.append(f"Unordered list items: {', '.join(lists['unordered'][:10])}")
        if lists.get('ordered'):
            summary.append(f"Ordered list items: {', '.join(lists['ordered'][:10])}")
        
        return "\n".join(summary)
    
    def _parse_llm_response (self, response:str) -> dict:
        try:
            response.strip()

            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            return json.loads(response)

        except json.JSONDecodeError: 
            logger.warning("LLM response is not valid JSON, returning as text")

            return {
                   "extracted_Text ": response,
                   "note":"LLM did not return any valid JSON"
               }
    def answer_question(self, question: str) -> str:
        """
        Answer a specific question about the scraped data
        
        Args:
            question: User's question about the data
            
        Returns:
            Answer from the AI
        """
        try:
            data_summary = self._prepare_data_summary()
            
            prompt = f"""You are analyzing scraped web data. Here's what was scraped:

{data_summary}

User Question: {question}

Please answer the question based on the scraped data. Be concise and accurate. If the information is not available in the data, say so."""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to answer question: {str(e)}")
            return f"Error: {str(e)}"  
    
    def suggest_extraction_fields(self) -> list:
        """
        AI suggests what fields can be extracted from the data
        
        Returns:
            List of suggested fields
        """
        try:
            data_summary = self._prepare_data_summary()
            
            prompt = f"""Analyze this scraped web data and suggest what useful information can be extracted:

{data_summary}

Provide a JSON list of field names that would be useful to extract. Each field should have a 'name' and 'description'.

Example format:
[
  {{"name": "product_names", "description": "List of product names"}},
  {{"name": "prices", "description": "Product prices"}}
]

Return ONLY valid JSON array."""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            suggestions = self._parse_llm_response(response.content)
            
            return suggestions if isinstance(suggestions, list) else []
            
        except Exception as e:
            logger.error(f"Failed to suggest fields: {str(e)}")
            return []

class AdvancedScrappingAgent:
    """Advanced agent with tool-based approach using latest LangChain"""

    def __init__(self, scraped_data: dict):
        self.scraped_data = scraped_data
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.1,
            max_tokens=4046
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()

    def _create_tools(self) -> list:
        """Create LangChain tools for the agent"""
        def get_page_title(query: str) -> str:
            return self.scraped_data.get('title', 'No title found')

        def get_all_links(query: str) -> str:
            links = self.scraped_data.get('links', [])
            return json.dumps([link['url'] for link in links[:20]], indent=2)

        def get_headings(query: str) -> str:
            headings = self.scraped_data.get('headings', {})
            return json.dumps(headings, indent=2)

        def get_text_content(query: str) -> str:
            text = self.scraped_data.get('text_content', '')
            return text[:2000]

        def search_in_content(query: str) -> str:
            text = self.scraped_data.get('text_content', '').lower()
            if query.lower() in text:
                index = text.find(query.lower())
                start = max(0, index - 100)
                end = min(len(text), index + 100)
                return f"Found: ...{text[start:end]}..."
            return "Not found in content"

        return [
            Tool(name="get_page_title", func=get_page_title, description="Get the title of the webpage"),
            Tool(name="get_all_links", func=get_all_links, description="Get all links found on the page"),
            Tool(name="get_headings", func=get_headings, description="Get all headings (h1-h6) from the page"),
            Tool(name="get_text_content", func=get_text_content, description="Get the main text content of the page"),
            Tool(name="search_in_content", func=search_in_content, description="Search for specific text in the page content. Input should be the search query."),
        ]

    def _create_agent(self):
        """Create the agent using new create_agent API"""
        tool_names = [tool.name for tool in self.tools]

        # Optional custom prompt template
        prompt_template = PromptTemplate.from_template("""Answer the following question as best you can using the available tools.

Question: {input}

You have access to these tools:
{tools}

Use this format:
Thought: Think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the question
""")

        # Create agent with new API
        agent = create_agent(
            llm=self.llm,
            tools=self.tools,
            system_prompt=prompt_template,  # pass custom ReAct-style prompt
            max_iterations=5,               # equivalent to old AgentExecutor
            verbose=True
        )
        return agent

    def run(self, query: str) -> str:
        """Run the agent with a query"""
        try:
            result = self.agent.invoke({"input": query})
            return result.get("output", "No output returned")
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            return f"Error: {str(e)}"