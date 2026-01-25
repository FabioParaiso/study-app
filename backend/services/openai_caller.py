from services.ports import OpenAIClientPort


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

        if model.startswith("gpt-5"):
            try:
                messages = [{"role": "user", "content": prompt}]
                if system_message:
                    messages.insert(0, {"role": "system", "content": system_message})

                effort = reasoning_effort or "none"
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "reasoning_effort": effort,
                }
                if effort == "none" and temperature is not None:
                    kwargs["temperature"] = temperature
                if seed is not None:
                    kwargs["seed"] = seed

                response = self.client.chat_completions_create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API Error (gpt-5 chat): {e}")
                return None

        try:
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": temperature,
            }
            if seed is not None:
                kwargs["seed"] = seed

            response = self.client.chat_completions_create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return None
