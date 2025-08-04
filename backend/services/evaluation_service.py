import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# RAGAS imports
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset import TestsetGenerator
from ragas import EvaluationDataset, evaluate, RunConfig
from ragas.metrics import (
    LLMContextRecall, 
    Faithfulness, 
    FactualCorrectness, 
    ResponseRelevancy, 
    ContextEntityRecall, 
    NoiseSensitivity
)

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class EvaluationService:
    """
    Service for evaluating system performance using RAGAS metrics
    """
    
    def __init__(self):
        self.generator_llm = None
        self.generator_embeddings = None
        self.evaluator_llm = None
        self.test_generator = None
        self.initialized = False
        self.evaluation_history = []
        
    async def initialize(self):
        """Initialize the evaluation service"""
        try:
            logger.info("Initializing Evaluation Service...")
            
            # Initialize generator components
            self.generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
            self.generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
            
            # Initialize evaluator
            self.evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))
            
            # Initialize test generator
            self.test_generator = TestsetGenerator(
                llm=self.generator_llm, 
                embedding_model=self.generator_embeddings
            )
            
            self.initialized = True
            logger.info("Evaluation Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Evaluation Service: {e}")
            raise
    
    async def generate_test_dataset(self, num_tests: int = 10, categories: List[str] = None) -> Dict[str, Any]:
        """Generate a test dataset for evaluation"""
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Generating test dataset with {num_tests} tests")
            
            # Create sample documents for testing
            sample_docs = self._create_sample_documents()
            
            # Generate test dataset
            dataset = await asyncio.to_thread(
                self.test_generator.generate_with_langchain_docs,
                sample_docs[:20],  # Use first 20 documents
                testset_size=num_tests
            )
            
            # Convert to pandas for easier handling
            df = dataset.to_pandas()
            
            # Extract test questions
            test_questions = df['eval_sample.user_input'].tolist()
            
            # Determine categories
            if categories is None:
                categories = self._extract_categories(test_questions)
            
            return {
                "test_questions": test_questions,
                "categories": categories,
                "total_tests": len(test_questions),
                "dataset": dataset,
                "difficulty_distribution": self._calculate_difficulty_distribution(test_questions)
            }
            
        except Exception as e:
            logger.error(f"Error generating test dataset: {e}")
            raise
    
    def _create_sample_documents(self) -> List[Document]:
        """Create sample documents for testing"""
        sample_docs = [
            Document(
                page_content="Wealth management involves comprehensive financial planning including investment management, tax planning, and retirement planning.",
                metadata={"source": "wealth_management_guide.pdf", "page": 1}
            ),
            Document(
                page_content="Investment strategies should be tailored to individual risk tolerance and financial goals.",
                metadata={"source": "investment_strategies.pdf", "page": 1}
            ),
            Document(
                page_content="Retirement planning requires careful consideration of income sources, expenses, and inflation.",
                metadata={"source": "retirement_planning.pdf", "page": 1}
            ),
            Document(
                page_content="Tax planning is essential for maximizing after-tax returns and minimizing tax liability.",
                metadata={"source": "tax_planning.pdf", "page": 1}
            ),
            Document(
                page_content="Risk management involves diversifying investments and maintaining appropriate asset allocation.",
                metadata={"source": "risk_management.pdf", "page": 1}
            )
        ]
        return sample_docs
    
    def _extract_categories(self, questions: List[str]) -> List[str]:
        """Extract categories from test questions"""
        categories = set()
        for question in questions:
            question_lower = question.lower()
            if any(keyword in question_lower for keyword in ['investment', 'portfolio']):
                categories.add('investment_advice')
            elif any(keyword in question_lower for keyword in ['retirement', 'planning']):
                categories.add('retirement_planning')
            elif any(keyword in question_lower for keyword in ['tax', 'taxation']):
                categories.add('tax_planning')
            elif any(keyword in question_lower for keyword in ['risk', 'diversification']):
                categories.add('risk_management')
            else:
                categories.add('general_advice')
        
        return list(categories)
    
    def _calculate_difficulty_distribution(self, questions: List[str]) -> Dict[str, int]:
        """Calculate difficulty distribution of questions"""
        distribution = {
            'easy': 0,
            'medium': 0,
            'hard': 0
        }
        
        for question in questions:
            # Simple heuristic for difficulty
            word_count = len(question.split())
            if word_count < 10:
                distribution['easy'] += 1
            elif word_count < 20:
                distribution['medium'] += 1
            else:
                distribution['hard'] += 1
        
        return distribution
    
    async def evaluate(self, test_questions: List[str], include_detailed_results: bool = True) -> Dict[str, Any]:
        """Evaluate system performance"""
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Evaluating system with {len(test_questions)} test questions")
            
            # Generate test dataset
            dataset_info = await self.generate_test_dataset(len(test_questions))
            dataset = dataset_info["dataset"]
            
            # Run evaluation
            custom_run_config = RunConfig(timeout=360)
            
            result = await asyncio.to_thread(
                evaluate,
                dataset=dataset,
                metrics=[
                    LLMContextRecall(), 
                    Faithfulness(), 
                    FactualCorrectness(), 
                    ResponseRelevancy(), 
                    ContextEntityRecall(), 
                    NoiseSensitivity()
                ],
                llm=self.evaluator_llm,
                run_config=custom_run_config
            )
            
            # Extract metrics
            metrics = {}
            for metric_name, metric_value in result.items():
                if hasattr(metric_value, 'score'):
                    metrics[metric_name] = metric_value.score
                else:
                    metrics[metric_name] = metric_value
            
            # Calculate overall score
            overall_score = sum(metrics.values()) / len(metrics) if metrics else 0.0
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics)
            
            # Store evaluation history
            evaluation_record = {
                "timestamp": datetime.now(),
                "metrics": metrics,
                "overall_score": overall_score,
                "test_questions_count": len(test_questions),
                "recommendations": recommendations
            }
            self.evaluation_history.append(evaluation_record)
            
            return {
                "metrics": metrics,
                "overall_score": overall_score,
                "recommendations": recommendations,
                "detailed_results": result if include_detailed_results else None,
                "evaluation_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Error in evaluation: {e}")
            raise
    
    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on evaluation metrics"""
        recommendations = []
        
        # Context Recall recommendations
        if metrics.get('context_recall', 1.0) < 0.7:
            recommendations.append("Improve context retrieval by optimizing vector search parameters")
        
        # Faithfulness recommendations
        if metrics.get('faithfulness', 1.0) < 0.8:
            recommendations.append("Enhance response generation to better align with retrieved context")
        
        # Factual Correctness recommendations
        if metrics.get('factual_correctness', 1.0) < 0.8:
            recommendations.append("Improve fact-checking and verification mechanisms")
        
        # Response Relevancy recommendations
        if metrics.get('response_relevancy', 1.0) < 0.8:
            recommendations.append("Optimize response generation to better address user queries")
        
        # Context Entity Recall recommendations
        if metrics.get('context_entity_recall', 1.0) < 0.7:
            recommendations.append("Enhance entity recognition and extraction from context")
        
        # Noise Sensitivity recommendations
        if metrics.get('noise_sensitivity', 1.0) < 0.8:
            recommendations.append("Improve robustness against noisy or irrelevant information")
        
        if not recommendations:
            recommendations.append("System performance is good across all metrics")
        
        return recommendations
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            if not self.evaluation_history:
                return {
                    "context_recall_score": 0.0,
                    "faithfulness_score": 0.0,
                    "factual_correctness_score": 0.0,
                    "response_relevancy_score": 0.0,
                    "overall_performance_score": 0.0,
                    "evaluation_timestamp": datetime.now(),
                    "test_dataset_size": 0,
                    "confidence_interval": None
                }
            
            # Get latest evaluation
            latest_eval = self.evaluation_history[-1]
            
            return {
                "context_recall_score": latest_eval["metrics"].get("context_recall", 0.0),
                "faithfulness_score": latest_eval["metrics"].get("faithfulness", 0.0),
                "factual_correctness_score": latest_eval["metrics"].get("factual_correctness", 0.0),
                "response_relevancy_score": latest_eval["metrics"].get("response_relevancy", 0.0),
                "overall_performance_score": latest_eval["overall_score"],
                "evaluation_timestamp": latest_eval["timestamp"],
                "test_dataset_size": latest_eval["test_questions_count"],
                "confidence_interval": self._calculate_confidence_interval(latest_eval["metrics"])
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            raise
    
    def _calculate_confidence_interval(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate confidence intervals for metrics"""
        # Simplified confidence interval calculation
        # In a real system, you'd use statistical methods
        return {
            "lower_bound": 0.8,
            "upper_bound": 0.95,
            "confidence_level": 0.95
        }
    
    async def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history"""
        try:
            return self.evaluation_history
        except Exception as e:
            logger.error(f"Error getting evaluation history: {e}")
            raise
    
    async def run_quick_evaluation(self, sample_questions: List[str] = None) -> Dict[str, Any]:
        """Run a quick evaluation with sample questions"""
        try:
            if sample_questions is None:
                sample_questions = [
                    "What are the key principles of wealth management?",
                    "How should I diversify my investment portfolio?",
                    "What tax considerations should I keep in mind for retirement planning?"
                ]
            
            return await self.evaluate(sample_questions, include_detailed_results=False)
            
        except Exception as e:
            logger.error(f"Error in quick evaluation: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health information"""
        try:
            return {
                "initialized": self.initialized,
                "generator_llm_available": self.generator_llm is not None,
                "evaluator_llm_available": self.evaluator_llm is not None,
                "test_generator_available": self.test_generator is not None,
                "evaluation_history_count": len(self.evaluation_history),
                "status": "healthy" if self.initialized else "not_initialized"
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "error",
                "error": str(e)
            } 