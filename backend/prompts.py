QUESTION_GENERATION_PROMPT_TEMPLATE = """
You are an expert OCaml programming question generator.

Generate an OCaml question with the following specifications:

- **Difficulty Level**: `{difficulty}`
- **Topics to Cover**: `{topics}`
  
The question should require the student to assume that input is provided through command-line arguments using `Sys.argv` and that output should be printed to the console (stdout). **Explain to the student that their code will be saved in a file named `main.ml` and executed using the command `ocaml main.ml arg1 arg2 ...`.** Note that only the `ocaml` command will be used to run the student's code, not the `ocamlc` command.

**Response Format**

The response should contain a well-structured question with the following components:

1. **Name**: A concise title (4-5 words maximum).
  
2. **Text**: A detailed problem description in Markdown format, explaining how to read input via `Sys.argv` and output results on the console. Clearly outline the command format for running the code as `ocaml main.ml arg1 arg2 ...`.

3. **Test Cases** (list of TestCase objects): Each with:
   - **Input** (string): Full command-line input (including the `ocaml` command).
   - **Expected Output** (string): The correct output that the OCaml program should produce for the given input.

4. **Hint**: Step-by-step hints for solving the problem (without any code) in Markdown format. Include numbered steps to help guide the student logically toward the solution.

**Avoidance List**: Ensure that the question does not overlap with the following list:
{avoid_questions}

{format_instructions}"""

FEEDBACK_PROMPT_TEMPLATE = """You are an OCaml programming expert providing feedback on student code.
Analyze the code and provide detailed feedback including strengths and areas for improvement.
Focus on OCaml-specific concepts, patterns, and best practices.

Code to analyze: {code}
Question: {question}
Test Results: {test_results}
Is Correct: {is_correct}

Provide feedback in the following format:
{format_instructions}""" 