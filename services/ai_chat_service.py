import time
from typing import List, Dict, Tuple
import random


class AIChatService:
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        
        self.responses = {
            "saludo": [
                "¡Hola! Soy Zamy, tu asistente de analítica. ¿En qué puedo ayudarte hoy?",
                "¡Bienvenido! Estoy aquí para ayudarte con tus datos y análisis. ¿Qué necesitas?",
                "¡Hola! ¿Cómo puedo asistirte con tu análisis de datos?",
            ],
            "ventas": [
                "Las ventas de este mes muestran un incremento del 15% comparado con el mes anterior. Los productos más vendidos son Diesel y General.",
                "Según los datos, la familia 'Llantas y rines' lidera con $4,758,897 en valorización, representando el 23.37% del total.",
                "El análisis de ventas indica una tendencia positiva. ¿Te gustaría ver un desglose por categoría o período?",
            ],
            "financiero": [
                "La tendencia financiera anual muestra estabilidad en los primeros meses con un incremento significativo hacia mediados de año.",
                "Los indicadores financieros están dentro del rango esperado. El margen promedio es del 28.44%.",
                "Basándome en los datos históricos, se proyecta un crecimiento sostenido para el próximo trimestre.",
            ],
            "clientes": [
                "La cartera de clientes actual muestra datos y tendencias positivas. ¿Te gustaría analizar algún segmento específico?",
                "Tenemos información detallada sobre el comportamiento de compra de los clientes. ¿Qué métrica te interesa?",
                "El análisis de clientes revela patrones interesantes de consumo. Puedo ayudarte a profundizar en cualquier segmento.",
            ],
            "ayuda": [
                "Puedo ayudarte con:\n• Análisis de ventas y tendencias\n• Reportes financieros\n• Información sobre clientes\n• Interpretación de gráficos\n• Comparativas de períodos\n\n¿Qué te gustaría saber?",
                "Estoy aquí para asistirte con análisis de datos, interpretación de métricas y responder preguntas sobre tu información financiera y operativa.",
                "Mis capacidades incluyen análisis de ventas, tendencias financieras, segmentación de clientes y más. ¿En qué área necesitas ayuda?",
            ],
            "default": [
                "Interesante pregunta. Basándome en los datos disponibles, puedo ayudarte a analizar esa información más a fondo.",
                "Entiendo tu consulta. ¿Podrías ser más específico para darte una respuesta más precisa?",
                "Puedo ayudarte con eso. ¿Te refieres a análisis de ventas, financiero o clientes?",
            ],
            "despedida": [
                "¡Hasta pronto! Aquí estaré cuando me necesites.",
                "¡Que tengas un excelente día! No dudes en consultarme cuando necesites analizar datos.",
                "¡Nos vemos! Estoy disponible 24/7 para ayudarte.",
            ],
            "agradecimiento": [
                "¡De nada! Para eso estoy aquí. ¿Algo más en lo que pueda ayudarte?",
                "¡Un placer ayudarte! Si necesitas más análisis, solo pregunta.",
                "¡Encantado de ayudar! ¿Hay algo más que quieras saber?",
            ],
        }
        
        self.keywords = {
            "saludo": ["hola", "buenos días", "buenas tardes", "buenas noches", "hey", "qué tal"],
            "ventas": ["ventas", "vendido", "productos", "ingresos", "facturación", "familia"],
            "financiero": ["financiero", "dinero", "margen", "ganancia", "utilidad", "tendencia"],
            "clientes": ["clientes", "cartera", "compradores", "segmento"],
            "ayuda": ["ayuda", "qué puedes hacer", "cómo funciona", "capacidades"],
            "despedida": ["adiós", "hasta luego", "nos vemos", "chao", "bye"],
            "agradecimiento": ["gracias", "muchas gracias", "te agradezco", "excelente"],
        }
    
    def detect_intent(self, message: str) -> str:
        message_lower = message.lower()
        
        for intent, keywords in self.keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "default"
    
    def get_response(self, user_message: str) -> Tuple[str, str]:
        intent = self.detect_intent(user_message)
        
        responses = self.responses.get(intent, self.responses["default"])
        response = random.choice(responses)
        
        timestamp = time.strftime("%H:%M")
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": timestamp
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })
        
        return response, timestamp
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_history
    
    def clear_history(self) -> None:
        self.conversation_history.clear()
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        return [
            {
                "icon": "tabler:chart-line",
                "label": "Ver tendencias de ventas",
                "action": "¿Cuáles son las tendencias de ventas actuales?"
            },
            {
                "icon": "tabler:report-money",
                "label": "Análisis financiero",
                "action": "Dame un resumen del análisis financiero"
            },
            {
                "icon": "tabler:users",
                "label": "Información de clientes",
                "action": "¿Qué me puedes decir sobre la cartera de clientes?"
            },
            {
                "icon": "tabler:help",
                "label": "¿Qué puedes hacer?",
                "action": "¿En qué puedes ayudarme?"
            },
        ]


ai_chat_service = AIChatService()