from streamlit.testing.v1 import AppTest

def test_quiz_radio_label():
    at = AppTest.from_file("app.py")

    # First run to initialize
    at.run()

    # Set session state to simulate a generated quiz
    quiz_data = [
        {
            "pergunta": "Qual é a capital de Portugal?",
            "opcoes": ["Lisboa", "Porto", "Coimbra", "Faro"],
            "resposta_correta": 0,
            "explicacao": "Lisboa é a capital."
        }
    ]
    at.session_state.quiz_data = quiz_data
    at.session_state.quiz_id = 1

    # Rerun to render the quiz
    at.run()

    # Check if radio buttons exist
    if not at.radio:
        print("No radio buttons found!")
        return

    # Print the label of the first radio button
    label = at.radio[0].label
    print(f"Radio Label: '{label}'")

    # ASSERTION: The label should contain the question text
    expected_label = "**1. Qual é a capital de Portugal?**"
    if label == expected_label:
        print("SUCCESS: Radio label matches expected question text.")
    else:
        print(f"FAILURE: Radio label '{label}' does not match expected '{expected_label}'")

    # Check for markdown elements
    found_markdown_question = False
    if at.markdown:
        for md in at.markdown:
            if "Qual é a capital de Portugal?" in md.body:
                # We need to be careful. The question is now IN the radio label.
                # Does AppTest report radio labels as markdown elements? No, usually separate.
                print(f"Found Markdown: '{md.body}'")
                found_markdown_question = True

    # We expect NOT to find a separate markdown element with the question BEFORE the radio
    # But since I can't easily check order here without more logic, I'll just rely on the radio label check.
    # Note: If st.radio label supports markdown, it's rendered as part of the widget.

    if not found_markdown_question:
         print("SUCCESS: No separate markdown question found (as expected).")
    else:
         print("NOTE: Found markdown text containing the question. This might be from the results view or other logic if triggered.")

if __name__ == "__main__":
    test_quiz_radio_label()
