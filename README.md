# KT_Generator

Repository of the code base for KT Generation process that we worked at Google Cloud, Searce and LifeSight GenAI Hackathon.

## Repo structure

- Code
- Presentation
- Readme.md

### Code

This folder contains the code base for the KT Generation process.

- KT Generator
    - `CodeParser.py`: This file contains the code to parse the code base and chunk it into logical code blocks (chunks).
    - `CarbonSnippets.py`: This file generates the `carbon.now` snippets for the code blocks.
    - `ResponseGenerator.py`: This file generates the explaination and the code summary using Llamaindex and PaLM LLM.
    - `DIDVideoGenerator.py`: This file generates the DID video avatar using the code explainations for all the chunks.
    - `CreateVideo.py`: This file stitches the final video using the videos and the code snippets and the summary.
    - `main.py`: This file is the main file that runs the entire process.
    - `config.py`: This file contains the necessary api keys, model names and other variable details to run main file.
    
### Usage

- Update details in `config.py` file and run `main.py` file to generate KT Video for your file.

```bash
python main.py
```
