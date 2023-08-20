# KT_Generator

Repository of the code base for KT Generation process that we worked at LifeSight, Google Cloud and Searce GenAI Hackathon.

## Repo structure

| -Code\
| -Presentation\
| -Readme.md

### Code

This folder contains the code base for the KT Generation process.

- `CodeParser.py`: This file contains the code to parse the code base and chunk it into logical code blocks (chunks).
- `CarbonSnippets.py`: This file generates the `carbon.now` snippets for the code blocks.
- `ResponseGenerator.py`: This file generates the explaination and the code summary using Llamaindex and PaLM LLM.
- `DIDVideoGenerator.py`: This file generates the DID video avatar using the code explainations for all the chunks.
- `CreateVideo.py`: This file stitches the final video using the videos and the code snippets and the summary.
- `main.py`: This file is the main file that runs the entire process.
