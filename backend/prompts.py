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

APPLICATION_DOMAINS = [
    "Banking System",
    "E-commerce System",
    "School Management System",
    "Vehicle Rental System", 
    "Game Development",
    "File System Management",
    "Online Learning Platform",
    "Restaurant Management System",
    "Healthcare Management System",
    "Smart Home System",
    "Inventory Management System", 
    "Hospital Management System",
    "University Library System",
    "Online Food Ordering System",
    "Pet Management System",
    "Zoo Management System",
    "Flight Reservation System",
    "E-learning Platform with Assessments",
    "Bookstore Management System",
    "Shopping Cart System",
    "Warehouse Management System",
    "Parking Management System",
    "Movie Ticket Booking System",
    "Sports Team Management System",
    "Real Estate Management System",
    "Travel Agency System",
    "Insurance Management System",
    "Social Media Platform",
    "Fitness Training Application",
    "Smart Farming System"
]

JAVA_QUESTION_GENERATION_PROMPT_TEMPLATE = """
You are an expert programmer specializing in Object-Oriented Programming (OOP). Your task is to generate a high-quality programming question to help undergraduate students practice for their OOP exams. The generated question should be relevant, engaging, and strictly adhere to the instructions provided.

### Steps to Generate the Question:

#### 1. **Application Domain**
Use the following domain to contextualize the programming problem:
`{domain}`

#### 2. **Create a Programming Question**
- Base the programming question on the **provided domain**.  
- Generate a **Java programming question** aligned with the following parameters:  
  - **Difficulty Level**: `{difficulty}`
  - **Topics to Cover**: `{topics}`  
- Ensure the question does **not involve file handling** or reading from external databases. 
- Explicitly include the following instructions in the problem description:
  - All required **user inputs should be read via command line arguments**.  
  - The driver class **must be named `Main`**, as the code will be saved as `Main.java` for testing.  

#### 4. **Test Case Independence** [Don't include this in the question description]
- The student code will be tested using multiple test cases, and for each test case, the `Main.java` file will be deleted and recreated.  
- Each test case must be **independent** of others.  
- Programs must not rely on maintaining state across multiple executions, as each test case will be run in isolation.  
- **Avoid interdependent test cases** like the following examples:  

---

#### **Examples of Invalid Interdependent Test Cases:**

1. **Bank Account Management:**  
   - **Input 1:** `"deposit 500"` → **Expected Output:** `Balance after deposit: 500`  
   - **Input 2:** `"withdraw 200"` → **WRONG - Assumes previous balance:** `Balance after withdrawal: 300`  

2. **Shopping Cart:**  
   - **Input 1:** `"add Apple 3"` → **Expected Output:** `Added Apple. Total price: $3`  
   - **Input 2:** `"add Banana 2"` → **WRONG - Assumes previous cart state:** `Added Banana. Total price: $5`  

3. **Parking Lot Management:**  
   - **Input 1:** `"park KA01AB1234"` → **Expected Output:** `Car KA01AB1234 parked. Slot 1 assigned.`  
   - **Input 2:** `"remove KA01AB1234"` → **WRONG - Assumes previous slot state:** `Slot 1 is now available.` 

#### 4. **Provide Output in the Following Format**:

1. **Name**: A short and concise title (4-5 words) that reflects the programming theme.  
2. **Text**: A detailed problem description in Markdown format. The description must:  
   - Clearly state the problem requirements and context.  
   - Include the instruction for naming the driver class as `Main` and for reading inputs from the command line.  
3. **Hint**: Provide step-by-step logical hints in Markdown format to guide the student toward solving the problem. Avoid writing code in the hints; focus on explaining the thought process.  

#### 5. **Avoidance List**
Ensure the generated question does **not overlap** with any of the following previously generated questions:  
{avoid_questions}

#### 6. **Formatting Instructions**
{format_instructions}
"""

JAVA_TEST_CASE_GENERATION_PROMPT_TEMPLATE = """
You are an expert programmer specializing in Object-Oriented Programming (OOP). Your task is to generate test cases for a Java programming question mentioned below.

### Question:
{question}

### Steps to Generate the Test Cases:

#### 1. **Test Case Independence**
- The student code will be tested using multiple test cases, and for each test case, the `Main.java` file will be deleted and recreated.  
- Each test case must be **independent** of others.  
- Programs must not rely on maintaining state across multiple executions, as each test case will be run in isolation.  
- **Avoid interdependent test cases** like the following examples:  

---

#### **Examples of Invalid Interdependent Test Cases:**

1. **Bank Account Management:**  
   - **Input 1:** `"deposit 500"` → **Expected Output:** `Balance after deposit: 500`  
   - **Input 2:** `"withdraw 200"` → **WRONG - Assumes previous balance:** `Balance after withdrawal: 300`  

2. **Shopping Cart:**  
   - **Input 1:** `"add Apple 3"` → **Expected Output:** `Added Apple. Total price: $3`  
   - **Input 2:** `"add Banana 2"` → **WRONG - Assumes previous cart state:** `Added Banana. Total price: $5`  

3. **Parking Lot Management:**  
   - **Input 1:** `"park KA01AB1234"` → **Expected Output:** `Car KA01AB1234 parked. Slot 1 assigned.`  
   - **Input 2:** `"remove KA01AB1234"` → **WRONG - Assumes previous slot state:** `Slot 1 is now available.`  

--- 

#### 2. **Provide Test Cases in the Following Format**:

1. **Test Cases**: Provide four independent test cases in the following structure:  
   - **Input**: The command line arguments as a single string (excluding the `java Main` command).  
   - **Expected Output**: The output for the given input as a single string.
   - Ensure that each test case is independent of others, and the program's output should only depend on the inputs provided during a single execution.

#### 3. **Formatting Instructions**
{format_instructions}
"""

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