import carbon
import asyncio
import os


def generate_carbon_snippets(code_list, save_path):
    async def generate_snippet(code, path):
        cb = carbon.Carbon()  # Create a Carbon instance
        opts = carbon.CarbonOptions(
            code=code,
            show_window_controls=False,
            language="python",
            theme="vscode",
            background_color=(171, 184, 195, 0),
        )  # Set the options for the image
        image = await cb.generate(opts)  # Generate the image
        await image.save(path)  # Save the image in png format

    for index, code in enumerate(code_list):
        path = os.path.join(save_path, f"image_{index}.png")
        asyncio.run(generate_snippet(code, path))
