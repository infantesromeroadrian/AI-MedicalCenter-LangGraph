from typing import Dict, List, Any, Optional, Set
import logging
from dataclasses import dataclass
import re

from src.models.data_models import AgentResponse, ConsensusResponse
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)

@dataclass
class ConsensusMetrics:
    """Metrics for evaluating consensus quality."""
    agreement_score: float  # 0-1: How much specialists agree
    confidence_weighted_score: float  # Weighted by individual confidence
    complementarity_score: float  # How well responses complement each other
    coherence_score: float  # Internal consistency of combined response
    urgency_consensus: Optional[str]  # Agreed urgency level

class ConsensusAgent:
    """Agent specialized in building intelligent consensus from multiple medical specialists."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the consensus agent."""
        self.llm_service = llm_service or LLMService()
    
    async def build_intelligent_consensus(
        self, 
        agent_responses: Dict[str, AgentResponse],
        emergency_status: Dict[str, Any],
        primary_specialty: str,
        user_query: str
    ) -> ConsensusResponse:
        """
        Build an intelligent consensus from multiple specialist responses.
        
        Args:
            agent_responses: Dictionary of responses from different specialists
            emergency_status: Emergency detection results
            primary_specialty: The primary recommended specialty
            user_query: Original user query for context
            
        Returns:
            Enhanced consensus response with intelligent synthesis
        """
        try:
            # Calculate consensus metrics
            metrics = self._calculate_consensus_metrics(agent_responses, user_query)
            
            # Identify key themes and conflicts
            themes = self._extract_key_themes(agent_responses)
            conflicts = self._identify_conflicts(agent_responses)
            
            # Generate synthesized response
            synthesized_response = await self._synthesize_responses(
                agent_responses, themes, conflicts, metrics, user_query
            )
            
            # Combine recommendations intelligently
            smart_recommendations = self._combine_recommendations(
                agent_responses, emergency_status, metrics
            )
            
            # Generate additional insights
            additional_insights = self._generate_additional_insights(
                agent_responses, primary_specialty, metrics
            )
            
            # Determine contributing specialties (exclude primary)
            contributing_specialties = [
                spec for spec in agent_responses.keys() 
                if spec != primary_specialty and agent_responses[spec].confidence > 0.3
            ]
            
            return ConsensusResponse(
                primary_specialty=primary_specialty,
                primary_response=synthesized_response,
                contributing_specialties=contributing_specialties,
                additional_insights=additional_insights,
                patient_recommendations=smart_recommendations,
                consensus_metrics=metrics.__dict__  # Include metrics for transparency
            )
            
        except Exception as e:
            logger.error(f"Error building intelligent consensus: {e}")
            # Fallback to simple consensus
            return self._fallback_consensus(agent_responses, primary_specialty)
    
    def _calculate_consensus_metrics(
        self, 
        agent_responses: Dict[str, AgentResponse],
        user_query: str
    ) -> ConsensusMetrics:
        """Calculate various metrics to evaluate consensus quality."""
        
        if len(agent_responses) < 2:
            return ConsensusMetrics(1.0, 1.0, 1.0, 1.0, None)
        
        # Agreement Score: Similarity between responses
        agreement_score = self._calculate_agreement_score(agent_responses)
        
        # Confidence Weighted Score: Average confidence weighted by response quality
        confidence_weighted_score = self._calculate_confidence_weighted_score(agent_responses)
        
        # Complementarity Score: How well responses complement each other
        complementarity_score = self._calculate_complementarity_score(agent_responses)
        
        # Coherence Score: Internal consistency
        coherence_score = self._calculate_coherence_score(agent_responses, user_query)
        
        # Urgency Consensus: Agreed urgency level
        urgency_consensus = self._determine_urgency_consensus(agent_responses)
        
        return ConsensusMetrics(
            agreement_score=agreement_score,
            confidence_weighted_score=confidence_weighted_score,
            complementarity_score=complementarity_score,
            coherence_score=coherence_score,
            urgency_consensus=urgency_consensus
        )
    
    def _calculate_agreement_score(self, agent_responses: Dict[str, AgentResponse]) -> float:
        """Calculate how much the specialists agree with each other."""
        responses = list(agent_responses.values())
        
        # Simple heuristic: count common medical terms and concepts
        agreement_indicators = []
        
        for i, resp1 in enumerate(responses):
            for j, resp2 in enumerate(responses[i+1:], i+1):
                # Extract key medical terms from both responses
                terms1 = self._extract_medical_terms(resp1.response)
                terms2 = self._extract_medical_terms(resp2.response)
                
                # Calculate Jaccard similarity
                if terms1 or terms2:
                    intersection = len(terms1.intersection(terms2))
                    union = len(terms1.union(terms2))
                    similarity = intersection / union if union > 0 else 0
                    agreement_indicators.append(similarity)
        
        return sum(agreement_indicators) / len(agreement_indicators) if agreement_indicators else 1.0
    
    def _calculate_confidence_weighted_score(self, agent_responses: Dict[str, AgentResponse]) -> float:
        """Calculate average confidence weighted by response characteristics."""
        if not agent_responses:
            return 0.0
        
        total_weighted_confidence = 0
        total_weight = 0
        
        for response in agent_responses.values():
            # Weight factors
            response_length_weight = min(1.0, len(response.response) / 200)  # Longer responses get more weight
            recommendation_weight = 1.2 if response.recommendations else 1.0
            source_weight = 1.1 if response.sources else 1.0
            
            total_weight_factor = response_length_weight * recommendation_weight * source_weight
            total_weighted_confidence += response.confidence * total_weight_factor
            total_weight += total_weight_factor
        
        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _calculate_complementarity_score(self, agent_responses: Dict[str, AgentResponse]) -> float:
        """Calculate how well responses complement each other (diversity of perspectives)."""
        if len(agent_responses) < 2:
            return 1.0
        
        # Check for different aspects covered by different specialists
        all_aspects = set()
        specialty_aspects = {}
        
        for specialty, response in agent_responses.items():
            aspects = self._extract_medical_aspects(response.response)
            specialty_aspects[specialty] = aspects
            all_aspects.update(aspects)
        
        if not all_aspects:
            return 0.5
        
        # Calculate how much each specialty contributes unique aspects
        unique_contributions = 0
        total_aspects = len(all_aspects)
        
        for specialty, aspects in specialty_aspects.items():
            # Count aspects that are unique or less common
            for aspect in aspects:
                occurrence_count = sum(1 for other_aspects in specialty_aspects.values() if aspect in other_aspects)
                uniqueness = 1.0 / occurrence_count  # More unique = higher score
                unique_contributions += uniqueness
        
        return min(1.0, unique_contributions / (total_aspects * len(agent_responses)))
    
    def _calculate_coherence_score(self, agent_responses: Dict[str, AgentResponse], user_query: str) -> float:
        """Calculate internal consistency and relevance to original query."""
        
        # Extract key symptoms/terms from user query
        query_terms = self._extract_medical_terms(user_query.lower())
        
        coherence_scores = []
        
        for response in agent_responses.values():
            response_terms = self._extract_medical_terms(response.response.lower())
            
            # Calculate relevance to original query
            if query_terms:
                relevance = len(query_terms.intersection(response_terms)) / len(query_terms)
            else:
                relevance = 0.5
            
            # Check for contradictory statements (simple heuristic)
            contradiction_penalty = self._detect_contradictions(response.response)
            
            # Final coherence score
            coherence = max(0.0, relevance - contradiction_penalty)
            coherence_scores.append(coherence)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
    
    def _determine_urgency_consensus(self, agent_responses: Dict[str, AgentResponse]) -> Optional[str]:
        """Determine consensus urgency level from all responses."""
        urgency_indicators = []
        
        for response in agent_responses.values():
            urgency = self._extract_urgency_level(response.response)
            if urgency:
                urgency_indicators.append(urgency)
        
        if not urgency_indicators:
            return None
        
        # Find most common urgency level
        urgency_counts = {}
        for urgency in urgency_indicators:
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
        
        return max(urgency_counts, key=urgency_counts.get)
    
    def _extract_medical_terms(self, text: str) -> Set[str]:
        """Extract medical terms from text."""
        # Enhanced medical term patterns
        medical_patterns = [
            r'\b(?:síntoma|diagnóstico|tratamiento|medicamento|enfermedad|trastorno|síndrome)\w*\b',
            r'\b(?:dolor|fiebre|náusea|vómito|diarrea|estreñimiento|fatiga|mareo)\w*\b',
            r'\b(?:presión|tensión|frecuencia|ritmo|pulso|temperatura)\w*\b',
            r'\b(?:análisis|examen|prueba|estudio|biopsia|radiografía)\w*\b',
            r'\b(?:cardíaco|neurológico|respiratorio|digestivo|renal|hepático)\w*\b',
            # English terms
            r'\b(?:symptom|diagnosis|treatment|medication|disease|disorder|syndrome)\w*\b',
            r'\b(?:pain|fever|nausea|vomit|diarrhea|constipation|fatigue|dizziness)\w*\b',
        ]
        
        terms = set()
        for pattern in medical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.update(match.lower() for match in matches)
        
        return terms
    
    def _extract_medical_aspects(self, text: str) -> Set[str]:
        """Extract medical aspects/categories from text."""
        aspect_patterns = {
            'diagnosis': r'\b(?:diagnóstico|posible|probable|sugiere|indica|parece)\b',
            'treatment': r'\b(?:tratamiento|terapia|medicamento|receta|prescrib)\b',
            'prevention': r'\b(?:prevención|prevenir|evitar|cuidado|hábito)\b',
            'symptom': r'\b(?:síntoma|manifestación|signo|presenta|siente)\b',
            'prognosis': r'\b(?:pronóstico|evolución|recuperación|tiempo|duración)\b',
            'emergency': r'\b(?:urgente|emergencia|inmediato|grave|crítico)\b'
        }
        
        aspects = set()
        for aspect, pattern in aspect_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                aspects.add(aspect)
        
        return aspects
    
    def _detect_contradictions(self, text: str) -> float:
        """Detect potential contradictions in response (simple heuristic)."""
        contradiction_patterns = [
            (r'\bno\s+es\b.*\bes\b', 0.3),  # "no es" followed by "es"
            (r'\bnormal\b.*\banormal\b', 0.4),  # normal and abnormal
            (r'\bseguro\b.*\bno\s+seguro\b', 0.3),  # sure and not sure
            (r'\brecomiendo\b.*\bno\s+recomiendo\b', 0.5),  # recommend and don't recommend
        ]
        
        penalty = 0.0
        for pattern, penalty_value in contradiction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                penalty += penalty_value
        
        return min(1.0, penalty)  # Cap at 1.0
    
    def _extract_urgency_level(self, text: str) -> Optional[str]:
        """Extract urgency level from response."""
        urgency_patterns = {
            'emergency': r'\b(?:emergencia|urgente|inmediato|crítico|grave|hospital)\b',
            'urgent': r'\b(?:pronto|rápido|sin demora|consulta pronto)\b', 
            'routine': r'\b(?:rutina|normal|consulta regular|no urgente)\b'
        }
        
        for level, pattern in urgency_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return level
        
        return None
    
    def _extract_key_themes(self, agent_responses: Dict[str, AgentResponse]) -> List[str]:
        """Extract key themes that appear across multiple responses."""
        all_terms = []
        for response in agent_responses.values():
            terms = self._extract_medical_terms(response.response)
            all_terms.extend(terms)
        
        # Count frequency of terms
        term_counts = {}
        for term in all_terms:
            term_counts[term] = term_counts.get(term, 0) + 1
        
        # Return terms that appear in multiple responses
        threshold = max(1, len(agent_responses) // 2)  # At least half of responses
        themes = [term for term, count in term_counts.items() if count >= threshold]
        
        return sorted(themes, key=lambda x: term_counts[x], reverse=True)[:10]
    
    def _identify_conflicts(self, agent_responses: Dict[str, AgentResponse]) -> List[Dict[str, Any]]:
        """Identify potential conflicts between specialist responses."""
        conflicts = []
        
        responses = list(agent_responses.items())
        
        for i, (spec1, resp1) in enumerate(responses):
            for j, (spec2, resp2) in enumerate(responses[i+1:], i+1):
                conflict_score = self._compare_responses_for_conflicts(resp1, resp2)
                
                if conflict_score > 0.3:  # Threshold for significant conflict
                    conflicts.append({
                        'specialists': [spec1, spec2],
                        'conflict_score': conflict_score,
                        'description': f"Potential disagreement between {spec1} and {spec2}"
                    })
        
        return conflicts
    
    def _compare_responses_for_conflicts(self, resp1: AgentResponse, resp2: AgentResponse) -> float:
        """Compare two responses to detect conflicts."""
        # Simple heuristic: look for opposing recommendations
        text1 = resp1.response.lower()
        text2 = resp2.response.lower()
        
        # Define opposing concepts
        opposing_pairs = [
            (['recomiendo', 'sugiero', 'aconsejo'], ['no recomiendo', 'evita', 'no aconsejo']),
            (['normal', 'típico', 'común'], ['anormal', 'atípico', 'raro']),
            (['urgente', 'inmediato'], ['no urgente', 'puede esperar']),
            (['grave', 'serio'], ['leve', 'menor', 'benigno'])
        ]
        
        conflict_score = 0.0
        
        for positive_terms, negative_terms in opposing_pairs:
            has_positive = any(term in text1 for term in positive_terms)
            has_negative = any(term in text2 for term in negative_terms)
            
            if has_positive and has_negative:
                conflict_score += 0.2
        
        return min(1.0, conflict_score)
    
    async def _synthesize_responses(
        self,
        agent_responses: Dict[str, AgentResponse],
        themes: List[str],
        conflicts: List[Dict[str, Any]],
        metrics: ConsensusMetrics,
        user_query: str
    ) -> str:
        """Generate a synthesized response using LLM."""
        
        # Prepare context for LLM synthesis
        specialist_summaries = []
        for specialty, response in agent_responses.items():
            summary = f"**{specialty.title()}**: {response.response[:300]}..."
            specialist_summaries.append(summary)
        
        synthesis_prompt = f"""
        Como coordinador médico, sintetiza las siguientes opiniones de especialistas en una respuesta coherente y completa.
        
        CONSULTA ORIGINAL: {user_query}
        
        OPINIONES DE ESPECIALISTAS:
        {chr(10).join(specialist_summaries)}
        
        TEMAS COMUNES IDENTIFICADOS: {', '.join(themes[:5])}
        
        MÉTRICAS DE CONSENSO:
        - Acuerdo entre especialistas: {metrics.agreement_score:.2f}
        - Confianza ponderada: {metrics.confidence_weighted_score:.2f}
        - Complementariedad: {metrics.complementarity_score:.2f}
        
        INSTRUCCIONES PARA LA SÍNTESIS:
        1. Crea una respuesta coherente que integre las perspectivas de todos los especialistas
        2. Destaca los puntos en los que hay consenso
        3. Aborda cualquier discrepancia de manera equilibrada
        4. Mantén un enfoque clínico profesional
        5. Proporciona una respuesta completa pero concisa
        6. Si hay conflictos, explica las diferentes perspectivas
        
        GENERA UNA RESPUESTA MÉDICA SINTÉTICA:
        """
        
        try:
            synthesized = await self.llm_service.generate_response(
                system_prompt="Eres un coordinador médico experto en sintetizar opiniones de múltiples especialistas.",
                user_prompt=synthesis_prompt
            )
            return synthesized
        except Exception as e:
            logger.error(f"Error in LLM synthesis: {e}")
            # Fallback: combine responses manually
            return self._manual_synthesis(agent_responses, themes)
    
    def _manual_synthesis(self, agent_responses: Dict[str, AgentResponse], themes: List[str]) -> str:
        """Manual fallback for response synthesis."""
        primary_response = next(iter(agent_responses.values())).response
        
        synthesis = f"{primary_response}\n\n"
        
        if len(agent_responses) > 1:
            synthesis += "**Perspectivas adicionales de otros especialistas:**\n"
            for specialty, response in list(agent_responses.items())[1:]:
                synthesis += f"- **{specialty.title()}**: {response.response[:150]}...\n"
        
        if themes:
            synthesis += f"\n**Aspectos clave identificados**: {', '.join(themes[:5])}"
        
        return synthesis
    
    def _combine_recommendations(
        self,
        agent_responses: Dict[str, AgentResponse],
        emergency_status: Dict[str, Any],
        metrics: ConsensusMetrics
    ) -> List[str]:
        """Intelligently combine recommendations from all specialists."""
        all_recommendations = []
        
        # Add emergency recommendations first if applicable
        if emergency_status.get("is_emergency"):
            all_recommendations.append(f"🚨 {emergency_status['recommendation']}")
        
        # Collect all recommendations from specialists
        specialist_recommendations = []
        for specialty, response in agent_responses.items():
            if response.recommendations:
                for rec in response.recommendations:
                    specialist_recommendations.append({
                        'text': rec,
                        'specialty': specialty,
                        'confidence': response.confidence
                    })
        
        # Deduplicate similar recommendations
        unique_recommendations = self._deduplicate_recommendations(specialist_recommendations)
        
        # Sort by confidence and importance
        unique_recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Add to final list with confidence indicators
        for rec in unique_recommendations[:8]:  # Limit to top 8
            confidence_indicator = "🔴" if rec['confidence'] > 0.8 else "🟡" if rec['confidence'] > 0.6 else "⚪"
            all_recommendations.append(f"{confidence_indicator} {rec['text']}")
        
        # Add consensus quality indicator
        if metrics.agreement_score > 0.8:
            all_recommendations.append("✅ Alto consenso entre especialistas en estas recomendaciones")
        elif metrics.agreement_score < 0.5:
            all_recommendations.append("⚠️ Opiniones divergentes entre especialistas - se recomienda consulta adicional")
        
        return all_recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar recommendations."""
        unique_recs = []
        
        for rec in recommendations:
            is_duplicate = False
            for existing in unique_recs:
                similarity = self._calculate_text_similarity(rec['text'], existing['text'])
                if similarity > 0.7:  # High similarity threshold
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if rec['confidence'] > existing['confidence']:
                        existing.update(rec)
                    break
            
            if not is_duplicate:
                unique_recs.append(rec)
        
        return unique_recs
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_additional_insights(
        self,
        agent_responses: Dict[str, AgentResponse],
        primary_specialty: str,
        metrics: ConsensusMetrics
    ) -> Dict[str, str]:
        """Generate additional insights from contributing specialists."""
        insights = {}
        
        for specialty, response in agent_responses.items():
            if specialty != primary_specialty and response.confidence > 0.4:
                # Extract unique insights from this specialty
                insight = self._extract_specialty_insight(response, specialty)
                if insight:
                    insights[specialty] = insight
        
        return insights
    
    def _extract_specialty_insight(self, response: AgentResponse, specialty: str) -> str:
        """Extract key insight from a specialist response."""
        # Take first 200 characters and last 100 characters to get main point and conclusion
        response_text = response.response
        
        if len(response_text) <= 300:
            return response_text
        
        insight = response_text[:200] + "..." + response_text[-100:]
        return insight
    
    def _fallback_consensus(
        self,
        agent_responses: Dict[str, AgentResponse],
        primary_specialty: str
    ) -> ConsensusResponse:
        """Fallback consensus method if intelligent consensus fails."""
        
        primary_response = agent_responses.get(primary_specialty)
        if not primary_response:
            primary_response = next(iter(agent_responses.values()))
            primary_specialty = next(iter(agent_responses.keys()))
        
        # Simple combination of all recommendations
        all_recommendations = []
        contributing_specialties = []
        additional_insights = {}
        
        for specialty, response in agent_responses.items():
            if specialty != primary_specialty:
                contributing_specialties.append(specialty)
                additional_insights[specialty] = response.response[:200] + "..."
            
            if response.recommendations:
                all_recommendations.extend(response.recommendations)
        
        return ConsensusResponse(
            primary_specialty=primary_specialty,
            primary_response=primary_response.response,
            contributing_specialties=contributing_specialties,
            additional_insights=additional_insights,
            patient_recommendations=all_recommendations[:10]  # Limit recommendations
        ) 