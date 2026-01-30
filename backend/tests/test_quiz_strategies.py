import pytest
import json
from modules.quizzes.prompts.builders import PromptBuilder, EvaluationPromptBuilder
from modules.quizzes.engine import MultipleChoiceStrategy, OpenEndedStrategy, ShortAnswerStrategy

NUM_QUESTIONS_MULTIPLE = 10

class TestQuizStrategies:
    
    @pytest.fixture
    def strategies(self):
        return {
            "multiple-choice": MultipleChoiceStrategy(),
            "short": ShortAnswerStrategy(),
            "open": OpenEndedStrategy()
        }

    def test_topic_instruction_empty(self, strategies):
        """Test strict logic: empty topics return empty instruction."""
        instr = PromptBuilder._build_topic_instruction([], ["Alpha"])
        assert "GLOBAL - MODO REVISÃO" in instr

    def test_topic_instruction_valid(self, strategies):
        """Test strict logic: valid topics generate instruction."""
        instr = PromptBuilder._build_topic_instruction(["Photosynthesis"], ["Cells"])
        assert "Photosynthesis" in instr
        assert "ESCOPO DE CONTEÚDO (FILTRADO)" in instr

    def test_priority_instruction(self, strategies):
        """Test priority topics instruction generation."""
        # Empty
        assert PromptBuilder._build_priority_instruction([]) == ""
        # Valid
        instr = PromptBuilder._build_priority_instruction(["Math"])
        assert "DIFICULDADE" in instr
        assert "Math" in instr

    def test_multiple_choice_prompt_structure(self, strategies):
        """Test that multiple choice prompt contains key instructions."""
        strat = strategies["multiple-choice"]
        prompt = strat.generate_prompt(
            text="Dummy text content about biology.",
            topics=["Cells"],
            priority_topics=["Nucleus"],
            material_concepts=["Cells", "Nucleus"]
        )
        
        # Check integrity of the prompt
        assert "Dummy text content" in prompt
        assert "Cells" in prompt
        assert "Nucleus" in prompt
        assert "correctIndex" in prompt  # JSON key specific to multiple choice
        assert "options" in prompt
        assert "PT-PT ESTRITO" in prompt

    def test_open_ended_prompt_structure(self, strategies):
        """Test that open ended prompt contains bloom taxonomy references."""
        strat = strategies["open"]
        prompt = strat.generate_prompt("Text", ["History"], material_concepts=["History"])
        
        assert "TAXONOMIA DE BLOOM" in prompt
        assert "COMPREENDER" in prompt
        assert "ANALISAR" in prompt
        # Should NOT have options
        assert "options" not in prompt

    def test_short_answer_prompt_structure(self, strategies):
        """Test short answer specific constraints."""
        strat = strategies["short"]
        prompt = strat.generate_prompt("Text", ["Grammar"], material_concepts=["Grammar"])
        
        assert "RESPOSTA CURTA" in prompt
        assert "SUJEITO e VERBO" in prompt
        assert "FRASE INTERROGATIVA" in prompt

    def test_parse_response_valid_json(self, strategies):
        """Test JSON parsing logic."""
        strat = strategies["multiple-choice"]
        valid_json = json.dumps({
            "questions": [{"q": 1}]
        })
        result = strat.parse_response(valid_json)
        assert len(result) == 1
        assert result[0]["q"] == 1

    def test_parse_response_invalid_json(self, strategies):
        """Test resilience to bad JSON."""
        strat = strategies["multiple-choice"]
        result = strat.parse_response("Invalid JSON")
        assert result == []

    def test_evaluation_prompt_generation(self, strategies):
        """Test evaluation prompt generation for open ended."""
        # Now using dedicated evaluation strategy
        from modules.quizzes.engine import OpenEndedEvaluationStrategy
        strat = OpenEndedEvaluationStrategy()
        prompt = strat.generate_evaluation_prompt("Context", "Question?", "Answer")
        
        assert "Context" in prompt
        assert "Question?" in prompt
        assert "Answer" in prompt
        assert "missing_points" in prompt
        assert "model_answer" in prompt
    
    def test_short_answer_evaluation_prompt(self):
        from modules.quizzes.engine import ShortAnswerEvaluationStrategy
        strat = ShortAnswerEvaluationStrategy()
        prompt = strat.generate_evaluation_prompt("Context", "Question?", "Answer")
        assert "Resposta Curta" in prompt
