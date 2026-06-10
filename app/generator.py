from typing import List, Dict, Any

from app.prompts import (
    ANSWER_TEMPLATE, 
    SOURCE_TEMPLATE, 
    REFUSAL_MESSAGES,
    OFFTOPIC_KEYWORDS
)


def is_offtopic(query: str) -> bool:
    """Проверяет, является ли запрос off-topic."""
    if not query:
        return True
    
    query_lower = query.lower()
    for keyword in OFFTOPIC_KEYWORDS:
        if keyword in query_lower:
            return True
    return False


def format_sources(results: List[Dict[str, Any]]) -> str:
    """Форматирует источники для вывода."""
    sources = []
    for r in results:
        source_name = r.get('name', r.get('doc_id', 'unknown'))
        if not source_name or source_name == 'unknown':
            source_name = f"Обращение #{r.get('doc_id', '?')}"
        
        sources.append(SOURCE_TEMPLATE.format(
            source_name=source_name,
            score=r.get('score', 0)
        ))
    return "\n".join(sources)


def generate_answer(query: str, results: List[Dict[str, Any]], threshold: float = None) -> Dict[str, Any]:
    """
    Генерирует ответ на основе найденных чанков
    """
    
    if threshold is None:
        threshold = 0.7
    
    # Проверка на пустой запрос
    if not query or not query.strip():
        return {
            'answer': REFUSAL_MESSAGES['empty_query'],
            'sources': '',
            'has_answer': False,
            'refusal_reason': 'empty_query'
        }
    
    # Проверка на off-topic
    if is_offtopic(query):
        return {
            'answer': REFUSAL_MESSAGES['off_topic'],
            'sources': '',
            'has_answer': False,
            'refusal_reason': 'off_topic'
        }
    
    # Нет результатов поиска
    if not results:
        return {
            'answer': REFUSAL_MESSAGES['no_context'],
            'sources': '',
            'has_answer': False,
            'refusal_reason': 'no_context'
        }
    
    # Фильтруем результаты по порогу
    relevant_results = [r for r in results if r.get('score', 0) >= threshold]
    
    if not relevant_results:
        return {
            'answer': REFUSAL_MESSAGES['low_score'],
            'sources': '',
            'has_answer': False,
            'refusal_reason': 'low_score'
        }
    
    # Формируем ответ из найденных чанков
    # Склеиваем текст из наиболее релевантных чанков
    answer_parts = []
    for r in relevant_results[:3]:  # максимум 3 чанка для ответа
        text = r.get('text', '')
        if text:
            # Обрезаем слишком длинный текст
            if len(text) > 500:
                text = text[:500] + "..."
            answer_parts.append(text)
    
    if not answer_parts:
        return {
            'answer': REFUSAL_MESSAGES['no_context'],
            'sources': '',
            'has_answer': False,
            'refusal_reason': 'no_context'
        }
    
    # Объединяем части ответа
    combined_answer = "\n\n".join(answer_parts)
    
    # Форматируем источники
    sources = format_sources(relevant_results[:3])
    
    return {
        'answer': combined_answer,
        'sources': sources,
        'has_answer': True,
        'refusal_reason': None
    }


def format_final_response(generation_result: Dict[str, Any]) -> str:
    """Форматирует финальный ответ для вывода в UI."""
    if generation_result['has_answer']:
        return ANSWER_TEMPLATE.format(
            answer=generation_result['answer'],
            sources=generation_result['sources']
        )
    else:
        return generation_result['answer']
