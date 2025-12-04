"""
NLP Complaint Classification System
Uses OpenRouter API (Claude/GPT) for intelligent complaint analysis
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


class ComplaintClassifier:
    """
    Advanced NLP-based complaint classification using LLM APIs
    Analyzes text complaints and classifies them intelligently
    """
    
    def __init__(self, api_key: str, model: str = "amazon/nova-2-lite-v1:free"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Complaint categories
        self.categories = {
            'pothole': {
                'keywords': ['pothole', 'hole', 'crater', 'ditch', 'depression', 'cavity'],
                'severity_indicators': ['large', 'deep', 'dangerous', 'severe', 'huge', 'massive']
            },
            'accident': {
                'keywords': ['accident', 'crash', 'collision', 'hit', 'injured', 'damage'],
                'severity_indicators': ['fatal', 'serious', 'major', 'severe', 'critical']
            },
            'traffic_congestion': {
                'keywords': ['traffic', 'congestion', 'jam', 'stuck', 'slow', 'gridlock'],
                'severity_indicators': ['heavy', 'severe', 'extreme', 'massive']
            },
            'road_damage': {
                'keywords': ['crack', 'damage', 'broken', 'deteriorate', 'surface', 'pavement'],
                'severity_indicators': ['extensive', 'severe', 'widespread', 'major']
            },
            'signal_malfunction': {
                'keywords': ['signal', 'light', 'traffic light', 'not working', 'broken', 'malfunction'],
                'severity_indicators': ['not working', 'broken', 'dangerous']
            },
            'debris': {
                'keywords': ['debris', 'obstacle', 'garbage', 'waste', 'blockage'],
                'severity_indicators': ['large', 'hazardous', 'blocking']
            },
            'poor_visibility': {
                'keywords': ['visibility', 'lighting', 'dark', 'street light', 'sign'],
                'severity_indicators': ['no', 'zero', 'poor', 'inadequate']
            },
            'emergency': {
                'keywords': ['emergency', 'urgent', 'immediate', 'danger', 'help'],
                'severity_indicators': ['immediate', 'critical', 'life-threatening']
            }
        }
    
    def classify_complaint(self, complaint_text: str, use_llm: bool = True) -> Dict:
        """
        Classify a complaint using NLP
        
        Args:
            complaint_text: The complaint text to analyze
            use_llm: Whether to use LLM API (True) or rule-based (False)
        
        Returns:
            Classification result with category, severity, urgency, etc.
        """
        if use_llm and self.api_key:
            return self._classify_with_llm(complaint_text)
        else:
            return self._classify_rule_based(complaint_text)
    
    def _classify_with_llm(self, complaint_text: str) -> Dict:
        """Classify using OpenRouter LLM API"""
        
        prompt = f"""Analyze this traffic/road complaint and provide a structured classification.

Complaint: "{complaint_text}"

Provide your analysis in the following JSON format:
{{
    "primary_category": "one of: pothole, accident, traffic_congestion, road_damage, signal_malfunction, debris, poor_visibility, emergency, other",
    "secondary_categories": ["list of any additional relevant categories"],
    "severity": "one of: low, medium, high, critical",
    "urgency": "one of: low, medium, high, immediate",
    "requires_immediate_action": true/false,
    "estimated_risk_level": 0-100,
    "affected_area_type": "one of: residential, highway, urban_center, rural, intersection",
    "description_summary": "brief summary of the issue",
    "recommended_action": "what should be done",
    "keywords_found": ["relevant keywords from complaint"],
    "sentiment": "one of: neutral, frustrated, angry, urgent, concerned"
}}

Respond ONLY with valid JSON, no other text."""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/sanchar-ai",
                "X-Title": "Sanchar AI Traffic Management"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON from response
                # Handle markdown code blocks if present
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                classification = json.loads(content)
                
                # Add metadata
                classification['classification_method'] = 'llm'
                classification['model_used'] = self.model
                classification['original_text'] = complaint_text
                classification['timestamp'] = datetime.now().isoformat()
                classification['confidence'] = 0.9  # High confidence for LLM
                
                return classification
            else:
                print(f"LLM API error: {response.status_code}")
                # Fall back to rule-based
                return self._classify_rule_based(complaint_text)
                
        except Exception as e:
            print(f"LLM classification error: {e}")
            # Fall back to rule-based
            return self._classify_rule_based(complaint_text)
    
    def _classify_rule_based(self, complaint_text: str) -> Dict:
        """Classify using rule-based keyword matching"""
        
        text_lower = complaint_text.lower()
        
        # Score each category
        category_scores = {}
        severity_indicators = []
        keywords_found = []
        
        for category, patterns in self.categories.items():
            score = 0
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in text_lower:
                    score += 2
                    keywords_found.append(keyword)
            
            # Check severity indicators
            for indicator in patterns['severity_indicators']:
                if indicator in text_lower:
                    score += 1
                    severity_indicators.append(indicator)
            
            if score > 0:
                category_scores[category] = score
        
        # Determine primary category
        if category_scores:
            primary_category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[primary_category] / 5, 0.95)
        else:
            primary_category = 'other'
            confidence = 0.3
        
        # Determine severity
        severity = self._calculate_severity(severity_indicators, text_lower)
        
        # Determine urgency
        urgency = self._calculate_urgency(primary_category, severity, text_lower)
        
        # Check for immediate action needed
        requires_immediate = (
            urgency == 'immediate' or
            severity == 'critical' or
            primary_category == 'emergency' or
            any(word in text_lower for word in ['emergency', 'urgent', 'danger', 'immediate'])
        )
        
        # Estimate risk level
        risk_level = self._calculate_risk_level(primary_category, severity, urgency)
        
        # Determine affected area type
        affected_area = self._determine_affected_area(text_lower)
        
        # Recommended action
        recommended_action = self._generate_recommendation(primary_category, severity, urgency)
        
        # Sentiment analysis (basic)
        sentiment = self._analyze_sentiment(text_lower)
        
        return {
            'primary_category': primary_category,
            'secondary_categories': [cat for cat in category_scores.keys() if cat != primary_category][:2],
            'severity': severity,
            'urgency': urgency,
            'requires_immediate_action': requires_immediate,
            'estimated_risk_level': risk_level,
            'affected_area_type': affected_area,
            'description_summary': complaint_text[:100] + '...' if len(complaint_text) > 100 else complaint_text,
            'recommended_action': recommended_action,
            'keywords_found': keywords_found[:5],
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'classification_method': 'rule_based',
            'original_text': complaint_text,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_severity(self, indicators: List[str], text: str) -> str:
        """Calculate severity level"""
        critical_words = ['fatal', 'death', 'life-threatening', 'critical', 'severe']
        high_words = ['dangerous', 'major', 'serious', 'large', 'deep']
        
        if any(word in text for word in critical_words):
            return 'critical'
        elif len(indicators) >= 2 or any(word in text for word in high_words):
            return 'high'
        elif len(indicators) == 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_urgency(self, category: str, severity: str, text: str) -> str:
        """Calculate urgency level"""
        immediate_words = ['immediate', 'urgent', 'emergency', 'now', 'asap']
        
        if any(word in text for word in immediate_words):
            return 'immediate'
        elif category in ['emergency', 'accident'] or severity == 'critical':
            return 'high'
        elif severity == 'high':
            return 'medium'
        else:
            return 'low'
    
    def _calculate_risk_level(self, category: str, severity: str, urgency: str) -> int:
        """Calculate risk level (0-100)"""
        base_risk = {
            'emergency': 90,
            'accident': 85,
            'pothole': 60,
            'signal_malfunction': 70,
            'traffic_congestion': 40,
            'road_damage': 55,
            'debris': 65,
            'poor_visibility': 50,
            'other': 30
        }.get(category, 30)
        
        severity_multiplier = {
            'critical': 1.3,
            'high': 1.15,
            'medium': 1.0,
            'low': 0.8
        }.get(severity, 1.0)
        
        urgency_multiplier = {
            'immediate': 1.2,
            'high': 1.1,
            'medium': 1.0,
            'low': 0.9
        }.get(urgency, 1.0)
        
        risk = int(base_risk * severity_multiplier * urgency_multiplier)
        return min(risk, 100)
    
    def _determine_affected_area(self, text: str) -> str:
        """Determine type of affected area"""
        if any(word in text for word in ['highway', 'expressway', 'freeway']):
            return 'highway'
        elif any(word in text for word in ['intersection', 'junction', 'crossing', 'signal']):
            return 'intersection'
        elif any(word in text for word in ['residential', 'neighborhood', 'colony', 'apartment']):
            return 'residential'
        elif any(word in text for word in ['city', 'downtown', 'center', 'commercial']):
            return 'urban_center'
        elif any(word in text for word in ['rural', 'village', 'countryside']):
            return 'rural'
        else:
            return 'urban_center'
    
    def _generate_recommendation(self, category: str, severity: str, urgency: str) -> str:
        """Generate action recommendation"""
        recommendations = {
            'emergency': 'Dispatch emergency response team immediately',
            'accident': 'Alert traffic police and emergency services. Clear area and redirect traffic.',
            'pothole': 'Schedule road maintenance crew for repair. Post warning signs if severe.',
            'signal_malfunction': 'Send technician for immediate repair. Deploy traffic police if needed.',
            'traffic_congestion': 'Analyze traffic patterns and adjust signal timing. Consider alternative routes.',
            'road_damage': 'Inspect damage extent and schedule repair. Install warning signs.',
            'debris': 'Send cleanup crew to clear obstruction immediately.',
            'poor_visibility': 'Install/repair lighting. Add reflective markers and signage.'
        }
        
        base_recommendation = recommendations.get(category, 'Investigate and take appropriate action')
        
        if urgency == 'immediate' or severity == 'critical':
            return f'URGENT: {base_recommendation}'
        else:
            return base_recommendation
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        angry_words = ['angry', 'furious', 'outraged', 'terrible', 'worst', 'unacceptable']
        frustrated_words = ['frustrated', 'annoyed', 'tired', 'fed up', 'disappointed']
        urgent_words = ['urgent', 'emergency', 'immediate', 'quickly', 'asap']
        concerned_words = ['worried', 'concerned', 'anxious', 'afraid', 'scared']
        
        if any(word in text for word in angry_words):
            return 'angry'
        elif any(word in text for word in frustrated_words):
            return 'frustrated'
        elif any(word in text for word in urgent_words):
            return 'urgent'
        elif any(word in text for word in concerned_words):
            return 'concerned'
        else:
            return 'neutral'
    
    def batch_classify(self, complaints: List[str]) -> List[Dict]:
        """Classify multiple complaints"""
        results = []
        
        for complaint in complaints:
            classification = self.classify_complaint(complaint, use_llm=False)
            results.append(classification)
        
        return results
    
    def get_statistics(self, classifications: List[Dict]) -> Dict:
        """Get statistics from multiple classifications"""
        if not classifications:
            return {}
        
        categories = [c['primary_category'] for c in classifications]
        severities = [c['severity'] for c in classifications]
        urgencies = [c['urgency'] for c in classifications]
        
        return {
            'total_complaints': len(classifications),
            'categories': {
                cat: categories.count(cat) for cat in set(categories)
            },
            'severities': {
                sev: severities.count(sev) for sev in set(severities)
            },
            'urgencies': {
                urg: urgencies.count(urg) for urg in set(urgencies)
            },
            'immediate_action_needed': sum(1 for c in classifications if c['requires_immediate_action']),
            'average_risk_level': sum(c['estimated_risk_level'] for c in classifications) / len(classifications),
            'high_risk_complaints': sum(1 for c in classifications if c['estimated_risk_level'] > 70)
        }
