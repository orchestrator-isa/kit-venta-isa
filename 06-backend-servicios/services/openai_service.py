import os
from typing import Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIService:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = "gpt-4o-mini"

    async def traducir_darija(self, texto: str, idioma_destino: str = "es") -> str:
        if not self.api_key:
            return f"[OpenAI no configurado] {texto}"

        # Fallback simple sin llamada real (para MVP)
        traducciones = {
            "es": {
                "salam": "¡Hola!",
                "chokran": "¡Gracias!",
                "bghit": "Quiero",
                "wakha": "Está bien / Vale",
                "ma3endich": "No tengo",
                "bzzaf": "Mucho",
                "mzyan": "Bien / Bueno",
                "khassni": "Necesito",
                "fin": "¿Dónde?",
                "bhal": "Como",
            },
            "fr": {
                "salam": "Bonjour",
                "chokran": "Merci",
                "bghit": "Je veux",
                "wakha": "D'accord",
                "ma3endich": "Je n'ai pas",
                "bzzaf": "Beaucoup",
                "mzyan": "Bien / Bon",
                "khassni": "J'ai besoin",
                "fin": "Où",
                "bhal": "Comme",
            }
        }

        palabras = texto.lower().split()
        traducidas = []
        for palabra in palabras:
            trad = traducciones.get(idioma_destino, {}).get(palabra, palabra)
            traducidas.append(trad)

        return " ".join(traducidas)

    async def detectar_intencion(self, mensaje: str) -> str:
        intenciones = {
            "reserva": ["reserva", "reserver", "حجز", "mesa", "table"],
            "pedido": ["pedido", "order", "طلب", "comprar", "acheter"],
            "consulta": ["precio", "prix", "سعر", "cuanto", "combien"],
            "reclamacion": ["problema", "problème", "مشكل", "queja", "réclamation"],
            "info": ["horario", "heure", "وقت", "ubicacion", "adresse", "عنوان"]
        }

        mensaje_lower = mensaje.lower()
        for intencion, palabras in intenciones.items():
            if any(p in mensaje_lower for p in palabras):
                return intencion
        return "general"

openai = OpenAIService()
