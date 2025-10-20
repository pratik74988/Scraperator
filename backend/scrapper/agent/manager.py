"""
Agent Manager - Coordinates between scraping and AI processing
"""
from .agent import ScrapingAgent, AdvancedScrappingAgent
from ..scraper import AutoScraper, ScrapperException
import logging

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages the scraping and AI processing pipeline"""
    
    @staticmethod
    def scrape_and_process(url: str, user_instructions: str = "", scraper_type: str = "auto", use_advanced_agent: bool = False):
        """
        Complete pipeline: Scrape URL -> Process with AI
        
        Args:
            url: Target URL to scrape
            user_instructions: What to extract
            scraper_type: 'auto', 'beautifulsoup', or 'selenium'
            use_advanced_agent: Use tool-based agent
            
        Returns:
            dict with raw_data and ai_processed_data
        """
        try:
            # Step 1: Scrape the website
            logger.info(f"Starting scrape for: {url}")
            raw_data = AutoScraper.scrape(url, scraper_type)
            logger.info("Scraping completed successfully")
            
            # Step 2: Process with AI (if instructions provided)
            ai_processed_data = None
            if user_instructions:
                logger.info("Processing data with AI agent")
                
                if use_advanced_agent:
                    agent = AdvancedScrappingAgent(raw_data)
                    ai_processed_data = {
                        "agent_response": agent.run(user_instructions)
                    }
                else:
                    agent = ScrapingAgent(raw_data)
                    ai_processed_data = agent.extract_structured_data(user_instructions)
                
                logger.info("AI processing completed")
            
            return {
                "status": "success",
                "raw_data": raw_data,
                "ai_processed_data": ai_processed_data,
                "url": url,
                "instructions": user_instructions
            }
            
        except ScrapperException as e:
            logger.error(f"Scraping failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_type": "scraping_error"
            }
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_type": "processing_error"
            }
    
    @staticmethod
    def answer_question_about_url(url: str, question: str, scraper_type: str = "auto"):
        """
        Scrape a URL and answer a specific question about it
        
        Args:
            url: Target URL
            question: Question to answer
            scraper_type: Type of scraper to use
            
        Returns:
            Answer from AI
        """
        try:
            # Scrape
            raw_data = AutoScraper.scrape(url, scraper_type)
            
            # Ask AI
            agent = ScrapingAgent(raw_data)
            answer = agent.answer_question(question)
            
            return {
                "status": "success",
                "question": question,
                "answer": answer,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Failed to answer question: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def get_extraction_suggestions(url: str, scraper_type: str = "auto"):
        """
        Scrape a URL and get AI suggestions for what can be extracted
        
        Args:
            url: Target URL
            scraper_type: Type of scraper to use
            
        Returns:
            List of suggested extraction fields
        """
        try:
            # Scrape
            raw_data = AutoScraper.scrape(url, scraper_type)
            
            # Get suggestions
            agent = ScrapingAgent(raw_data)
            suggestions = agent.suggest_extraction_fields()
            
            return {
                "status": "success",
                "url": url,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }