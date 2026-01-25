from modules.common.ports import OpenAIClientPort


class OpenAICaller:
    def __init__(self, client: OpenAIClientPort | None):
        self.client = client

    def call(
        self,
        prompt: str,
        system_message: str,
        model: str,
        temperature: float = 0.7,
        seed: int | None = None,
        reasoning_effort: str | None = None
    ) -> str | None:
        if not self.client:
            return None

        kwargs = {
            "model": model,
            "response_format": {"type": "json_object"},
        }
        
        # O1 models (aka gpt-5 or reasoning models) typically don't support system roles or temperature in standard ways
        # This check isolates that logic branch.
        is_reasoning_model = model.startswith("gpt-5") or model.startswith("o1")

        if is_reasoning_model:
            # Reasoning models use 'developer' role or sometimes just user messages, 
            # and 'reasoning_effort' instead of temperature/max_tokens sometimes.
            # We stick to simple user message for now as per previous logic.
            messages = [{"role": "user", "content": prompt}]
            if system_message:
                messages.insert(0, {"role": "system", "content": system_message})
            
            kwargs["messages"] = messages
            kwargs["reasoning_effort"] = reasoning_effort or "none"
            if seed is not None:
                kwargs["seed"] = seed
                
            # Temperature is not supported for reasoning_effort != none usually
            if kwargs["reasoning_effort"] == "none" and temperature is not None:
                 kwargs["temperature"] = temperature

        else:
            # Standard GPT-4 models
            kwargs["messages"] = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            kwargs["temperature"] = temperature
            if seed is not None:
                kwargs["seed"] = seed

        try:
            response = self.client.chat_completions_create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            # In a real system, use a logger, not print
            print(f"OpenAI API Error ({model}): {e}")
            return None
