OCAML_QUESTION_GENERATION_PROMPT_TEMPLATE = """
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

JAVA_QUESTION_GENERATION_PROMPT_TEMPLATE = """
You are an expert Java programming question generator.

Generate a Java question with the following specifications:

- **Difficulty Level**: `{difficulty}`
- **Topics to Cover**: `{topics}`
  
The question should require the student to write a Java program with a Main class containing a main method. **Explain to the student that their code will be saved in a file named `Main.java` and executed using the commands `javac Main.java` followed by `java Main arg1 arg2 ...`.** The program should handle command-line arguments using the `args` parameter of the main method.

**Response Format**

The response should contain a well-structured question with the following components:

1. **Name**: A concise title (4-5 words maximum).
  
2. **Text**: A detailed problem description in Markdown format, explaining how to use command-line arguments via the `args` array and output results using `System.out.println()`. Clearly outline the command format for running the code.

3. **Test Cases** (list of TestCase objects): Each with:
   - **Input** (string): Full command-line input (including the `java Main` command).
   - **Expected Output** (string): The correct output that the Java program should produce for the given input.

4. **Hint**: Step-by-step hints for solving the problem (without any code) in Markdown format. Include numbered steps to help guide the student logically toward the solution.

**Avoidance List**: Ensure that the question does not overlap with the following list:
{avoid_questions}

{format_instructions}"""

C_QUESTION_GENERATION_PROMPT_TEMPLATE = """
You are an expert C programming question generator.

Generate a C question with the following specifications:

- **Difficulty Level**: `{difficulty}`
- **Topics to Cover**: `{topics}`
  
The question should require the student to write a C program that uses argc and argv for command-line arguments. **Explain to the student that their code will be saved in a file named `main.c` and executed using the commands `gcc main.c -o main` followed by `./main arg1 arg2 ...`.** The program should handle command-line arguments using argc and argv parameters of the main function.

**Response Format**

The response should contain a well-structured question with the following components:

1. **Name**: A concise title (4-5 words maximum).
  
2. **Text**: A detailed problem description in Markdown format, explaining how to use command-line arguments via argc/argv and output results using printf(). Clearly outline the command format for running the code.

3. **Test Cases** (list of TestCase objects): Each with:
   - **Input** (string): Full command-line input (including the `./main` command).
   - **Expected Output** (string): The correct output that the C program should produce for the given input.

4. **Hint**: Step-by-step hints for solving the problem (without any code) in Markdown format. Include numbered steps to help guide the student logically toward the solution.

**Avoidance List**: Ensure that the question does not overlap with the following list:
{avoid_questions}

{format_instructions}"""

QUESTION_GENERATION_PROMPT_TEMPLATES = {
    "ocaml": OCAML_QUESTION_GENERATION_PROMPT_TEMPLATE,
    "java": JAVA_QUESTION_GENERATION_PROMPT_TEMPLATE,
    "c": C_QUESTION_GENERATION_PROMPT_TEMPLATE
}


OCAML_FEEDBACK_PROMPT_TEMPLATE = """You are an OCaml programming expert providing feedback on student code.
Analyze the code and provide detailed feedback including strengths and areas for improvement.
Focus on OCaml-specific concepts, patterns, and best practices.

Code to analyze: {code}
Question: {question}
Test Results: {test_results}
Is Correct: {is_correct}

Provide feedback in the following format:
{format_instructions}"""

JAVA_FEEDBACK_PROMPT_TEMPLATE = """You are a Java programming expert providing feedback on student code.
Analyze the code and provide detailed feedback including strengths and areas for improvement.
Focus on Java-specific concepts like object-oriented design, proper class structure, and Java best practices.

Code to analyze: {code}
Question: {question}
Test Results: {test_results}
Is Correct: {is_correct}

Provide feedback in the following format:
{format_instructions}"""

C_FEEDBACK_PROMPT_TEMPLATE = """You are a C programming expert providing feedback on student code.
Analyze the code and provide detailed feedback including strengths and areas for improvement.
Focus on C-specific concepts like memory management, pointer usage, and C best practices.

Code to analyze: {code}
Question: {question}
Test Results: {test_results}
Is Correct: {is_correct}

Provide feedback in the following format:
{format_instructions}"""

FEEDBACK_PROMPT_TEMPLATES = {
    "ocaml": OCAML_FEEDBACK_PROMPT_TEMPLATE,
    "java": JAVA_FEEDBACK_PROMPT_TEMPLATE,
    "c": C_FEEDBACK_PROMPT_TEMPLATE
}