from services.analyze.gemini import GeminiAnalyzer
from services.evaluate.gemini import GeminiEvaluator
from services.evaluate.local_llm import OllamaEvaluator
from storage.mongodb import MongoDBStorage

ANALYZER_REGISTRY = {
    "gemini": GeminiAnalyzer,
}

EVALUATOR_REGISTRY = {
    "gemini": GeminiEvaluator,
    "ollama": OllamaEvaluator,
}

STORAGE_REGISTRY = {
    "mongodb": MongoDBStorage,
}