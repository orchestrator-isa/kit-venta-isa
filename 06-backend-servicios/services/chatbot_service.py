import json
import os
from typing import Dict, Any, Optional

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
BOT_CONFIGS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "bot-configs")

class ChatbotService:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.bot_configs = {}
        self._load_bot_configs()

    def _load_bot_configs(self):
        if os.path.exists(BOT_CONFIGS_PATH):
            for filename in os.listdir(BOT_CONFIGS_PATH):
                if filename.endswith(".json"):
                    bot_id = filename.replace(".json", "")
                    with open(os.path.join(BOT_CONFIGS_PATH, filename), "r", encoding="utf-8") as f:
                        self.bot_configs[bot_id] = json.load(f)

    def get_bot_config(self, bot_id: str) -> Optional[Dict[str, Any]]:
        return self.bot_configs.get(bot_id)

    def get_pack_info(self, pack_key: str) -> Optional[Dict[str, Any]]:
        return self.config.get("packs", {}).get(pack_key)

    def get_segmento(self, facturacion_mensual: float) -> str:
        seg = self.config["segmentacion"]["p1_facturacion"]
        if facturacion_mensual < seg["pobre"]["max"]:
            return "pobre"
        elif facturacion_mensual < seg["pobre-medio"]["max"]:
            return "pobre-medio"
        elif facturacion_mensual < seg["estandar"]["max"]:
            return "estandar"
        else:
            return "premium"

    def get_respuesta_rapida(self, bot_id: str, tipo: str) -> str:
        config = self.get_bot_config(bot_id)
        if not config:
            return "¡Hola! ¿En qué puedo ayudarte?"
        return config.get("respuestas_rapidas", {}).get(tipo, "¿En qué puedo ayudarte?")

    def procesar_mensaje(self, bot_id: str, telefono: str, mensaje: str, contexto: Dict = None) -> Dict[str, Any]:
        config = self.get_bot_config(bot_id)
        if not config:
            return {"respuesta": "Bot no configurado.", "accion": None}

        mensaje_lower = mensaje.lower().strip()

        # Respuestas rápidas por palabra clave
        if any(p in mensaje_lower for p in ["hola", "salam", "bonjour", "hi"]):
            return {"respuesta": self.get_respuesta_rapida(bot_id, "bienvenida"), "accion": "bienvenida"}

        if any(p in mensaje_lower for p in ["menu", "menú", "carte", "طعام"]):
            return {"respuesta": self.get_respuesta_rapida(bot_id, "menu"), "accion": "mostrar_menu"}

        if any(p in mensaje_lower for p in ["reserva", "reserver", "حجز", "mesa"]):
            return {"respuesta": self.get_respuesta_rapida(bot_id, "reserva"), "accion": "iniciar_reserva", "fase": "res_p"}

        if any(p in mensaje_lower for p in ["pedido", "order", "طلب", "comprar"]):
            return {"respuesta": self.get_respuesta_rapida(bot_id, "pedido"), "accion": "iniciar_pedido"}

        if any(p in mensaje_lower for p in ["horario", "hora", "heure", "وقت"]):
            return {"respuesta": self.get_respuesta_rapida(bot_id, "horario"), "accion": "info_horario"}

        if any(p in mensaje_lower for p in ["ubicacion", "donde", "ou", "موقع", "mapa"]):
            return {"respuesta": self.get_respuesta_rapida(bot_id, "ubicacion"), "accion": "info_ubicacion"}

        return {"respuesta": "No entendí bien. ¿Puedes reformular? También puedes decirme: menú, reserva, pedido, horario o ubicación.", "accion": "desconocido"}

chatbot = ChatbotService()
