import ast

class code_parser:

    def extract_classes_from_code(self, code: str):
        parsed_code = ast.parse(code)
        classes = []
        for node in parsed_code.body:
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "class_name": node.name,
                    "docstring": ast.get_docstring(node),
                    "init_method": None,
                    "methods": [],
                }

                for class_node in node.body:
                    if isinstance(class_node, ast.FunctionDef):
                        if class_node.name == "__init__":
                            init_method_code = ast.get_source_segment(code, class_node)
                            class_info["init_method"] = init_method_code
                        else:
                            method_code = ast.get_source_segment(code, class_node)
                            class_info["methods"].append(method_code)
                classes.append(class_info)

        output = []
        for class_info in classes:
            class_info["docstring"] = (
                "" if class_info["docstring"] is None else class_info["docstring"]
            )
            class_information = f"Class {class_info['class_name']} \n {class_info['docstring']} \n {class_info['init_method']}"
            output.append(class_information)
            for method in class_info["methods"]:
                output.append(method)

        return output

    def extract_elements(self, source: str):
        node = ast.parse(source)

        def is_at_module_level(n):
            for parent in ast.walk(n):
                if isinstance(parent, (ast.FunctionDef, ast.ClassDef, ast.With)):
                    return False
            return True

        elements = []

        imports_block = ""

        for n in ast.walk(node):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                if is_at_module_level(n):
                    start_line = n.lineno - 1
                    end_line = n.lineno
                    imports_block += "".join(source.splitlines(True)[start_line:end_line])
            elif isinstance(n, ast.FunctionDef):
                if is_at_module_level(n):  # Ensure the function is not within a class
                    start_line = n.lineno - 1
                    end_line = max(
                        (x.lineno for x in ast.walk(n) if hasattr(x, "lineno")), default=n.lineno
                    )
                    elements.append("".join(source.splitlines(True)[start_line:end_line]))
            elif isinstance(n, ast.ClassDef):
                start_line = n.lineno - 1
                end_line = max(
                    (x.lineno for x in ast.walk(n) if hasattr(x, "lineno")), default=n.lineno
                )
                class_code = "".join(source.splitlines(True)[start_line:end_line])
                if (end_line - start_line) > 10:
                    classes_functions = self.extract_classes_from_code(class_code)
                    elements.extend(classes_functions)
                else:
                    elements.append(class_code)
            # Add more handlers if you need to extract more types of nodes

        # Prepend the imports block if there were any imports
        if imports_block:
            elements.insert(0, imports_block)

        return elements


if __name__ == "__main__":
    # Provide the code directly as a string or read from a file
    # If you are reading from a file:
    with open("test_code_google_calender.py", "r") as f:
        source = f.read()

    extracted_elements = code_parser().extract_elements(source)
