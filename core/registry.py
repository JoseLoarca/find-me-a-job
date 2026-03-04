from services.analyze.gemini import GeminiAnalyzer
from services.evaluate.gemini import GeminiEvaluator
from storage.mongodb import MongoDBStorage

ANALYZER_REGISTRY = {
    "gemini": GeminiAnalyzer,
}

EVALUATOR_REGISTRY = {
    "gemini": GeminiEvaluator,
}

STORAGE_REGISTRY = {
    "mongodb": MongoDBStorage,
}