import json
from groq import Groq
from app.config import settings

# Campos necessários para petição de divórcio
DIVORCE_FIELDS = {
    "author_name": "nome completo do requerente (quem entra com o processo)",
    "author_cpf": "CPF do requerente",
    "author_address": "endereço completo do requerente",
    "defendant_name": "nome completo do requerido (outro cônjuge)",
    "defendant_cpf": "CPF do requerido",
    "marriage_date": "data do casamento (DD/MM/AAAA)",
    "marriage_regime": "regime de bens (comunhão parcial, comunhão universal, separação total ou participação final nos aquestos)",
    "has_children": "tem filhos menores de 18 anos? (sim/não — se sim, informe quantos e as idades)",
    "has_assets": "tem bens a partilhar? (sim/não — se sim, descreva brevemente)",
}

SYSTEM_PROMPT = """Você é um assistente jurídico amigável que ajuda a coletar informações para uma petição de divórcio.

Sua tarefa é coletar os seguintes dados, um por vez, de forma natural e amigável:
{fields_description}

Regras importantes:
- Faça UMA pergunta por vez
- Use linguagem simples, sem juridiquês
- Confirme o dado antes de avançar quando não ficou claro
- Quando receber um dado, extraia-o de forma estruturada
- Após cada resposta do usuário, retorne um JSON com dois campos:
  1. "message": sua resposta para o usuário (próxima pergunta ou confirmação)
  2. "extracted": dicionário com os dados extraídos desta mensagem (apenas os novos dados, não repita os anteriores)

Exemplo de retorno:
{{"message": "Entendido! E qual é o CPF do Sr. João?", "extracted": {{"author_name": "João da Silva"}}}}

Se o usuário fornecer um dado inválido (ex: CPF com formato errado), peça novamente de forma gentil.
Quando todos os dados estiverem coletados, inclua "collection_complete": true no JSON."""


class ChatEngine:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)

    def get_missing_fields(self, collected_data: dict) -> list[str]:
        return [field for field in DIVORCE_FIELDS if field not in collected_data or not collected_data[field]]

    def is_collection_complete(self, collected_data: dict) -> bool:
        return len(self.get_missing_fields(collected_data)) == 0

    def _build_system_prompt(self) -> str:
        fields_desc = "\n".join(
            f"- {field}: {description}"
            for field, description in DIVORCE_FIELDS.items()
        )
        return SYSTEM_PROMPT.format(fields_description=fields_desc)

    def process_message(
        self,
        user_message: str,
        history: list[dict],
        collected_data: dict,
    ) -> tuple[str, dict]:
        """
        Processa uma mensagem do usuário.
        Retorna (resposta_texto, dados_coletados_atualizados).
        """
        messages = [{"role": "system", "content": self._build_system_prompt()}]

        if collected_data:
            context = f"Dados já coletados: {json.dumps(collected_data, ensure_ascii=False)}"
            messages.append({"role": "system", "content": context})

        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )

        raw_content = response.choices[0].message.content.strip()

        # Tenta parsear JSON da resposta
        try:
            # Remove possível markdown ```json ... ```
            if "```" in raw_content:
                raw_content = raw_content.split("```")[1]
                if raw_content.startswith("json"):
                    raw_content = raw_content[4:]

            parsed = json.loads(raw_content)
            message = parsed.get("message", raw_content)
            extracted = parsed.get("extracted", {})
            updated_data = {**collected_data, **extracted}
        except (json.JSONDecodeError, KeyError):
            # Se não conseguir parsear, usa o texto como resposta e não extrai dados
            message = raw_content
            updated_data = collected_data

        return message, updated_data
